import re
from datetime import date, datetime

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, MethodNotAllowed

from app import db
from app.models import Student, VALID_ENROLLMENT_STATUSES
from app.routes import students_bp


# --- Validation ---

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_student_data(data, is_update=False):
    """Validate student input data. Returns (cleaned_data, errors) tuple."""
    errors = []

    if not isinstance(data, dict):
        return None, ["Request body must be a JSON object."]

    # Required fields
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    date_of_birth = data.get("date_of_birth")
    enrollment_status = data.get("enrollment_status")

    # first_name
    if first_name is None or (isinstance(first_name, str) and not first_name.strip()):
        errors.append("first_name is required and cannot be empty.")
    elif not isinstance(first_name, str):
        errors.append("first_name must be a string.")

    # last_name
    if last_name is None or (isinstance(last_name, str) and not last_name.strip()):
        errors.append("last_name is required and cannot be empty.")
    elif not isinstance(last_name, str):
        errors.append("last_name must be a string.")

    # email
    if email is None or (isinstance(email, str) and not email.strip()):
        errors.append("email is required and cannot be empty.")
    elif not isinstance(email, str):
        errors.append("email must be a string.")
    elif not EMAIL_REGEX.match(email.strip()):
        errors.append("email must be a valid email address.")

    # date_of_birth
    parsed_dob = None
    if date_of_birth is None or (isinstance(date_of_birth, str) and not date_of_birth.strip()):
        errors.append("date_of_birth is required.")
    elif not isinstance(date_of_birth, str):
        errors.append("date_of_birth must be a string in YYYY-MM-DD format.")
    else:
        try:
            parsed_dob = datetime.strptime(date_of_birth.strip(), "%Y-%m-%d").date()
            if parsed_dob > date.today():
                errors.append("date_of_birth cannot be in the future.")
        except ValueError:
            errors.append("date_of_birth must be a valid date in YYYY-MM-DD format.")

    # enrollment_status
    if enrollment_status is None:
        errors.append("enrollment_status is required.")
    elif not isinstance(enrollment_status, str):
        errors.append("enrollment_status must be a string.")
    elif enrollment_status.strip().lower() not in VALID_ENROLLMENT_STATUSES:
        errors.append(
            f"enrollment_status must be one of: {', '.join(sorted(VALID_ENROLLMENT_STATUSES))}."
        )

    if errors:
        return None, errors

    cleaned = {
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "email": email.strip().lower(),
        "date_of_birth": parsed_dob,
        "enrollment_status": enrollment_status.strip().lower(),
    }
    return cleaned, []


# --- Error Handlers ---

@students_bp.app_errorhandler(NotFound)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404


@students_bp.app_errorhandler(MethodNotAllowed)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed."}), 405


# --- Routes ---

@students_bp.route("", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    cleaned, errors = validate_student_data(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    student = Student(
        first_name=cleaned["first_name"],
        last_name=cleaned["last_name"],
        email=cleaned["email"],
        date_of_birth=cleaned["date_of_birth"],
        enrollment_status=cleaned["enrollment_status"],
    )

    try:
        db.session.add(student)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A student with this email already exists."}), 409

    return jsonify(student.to_dict()), 201


@students_bp.route("", methods=["GET"])
def list_students():
    # Pagination params
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except (ValueError, TypeError):
        return jsonify({"error": "page and per_page must be positive integers."}), 400

    if page < 1 or per_page < 1:
        return jsonify({"error": "page and per_page must be positive integers."}), 400

    if per_page > 100:
        per_page = 100

    # Filtering
    query = Student.query
    enrollment_status = request.args.get("enrollment_status")
    if enrollment_status:
        status = enrollment_status.strip().lower()
        if status not in VALID_ENROLLMENT_STATUSES:
            return jsonify({
                "error": f"Invalid enrollment_status filter. Must be one of: {', '.join(sorted(VALID_ENROLLMENT_STATUSES))}."
            }), 400
        query = query.filter_by(enrollment_status=status)

    # Order by most recently created first
    query = query.order_by(Student.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "students": [s.to_dict() for s in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }), 200


@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"error": "Student not found."}), 404
    return jsonify(student.to_dict()), 200


@students_bp.route("/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"error": "Student not found."}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    cleaned, errors = validate_student_data(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    # Check if email is being changed to one that already exists
    if cleaned["email"] != student.email:
        existing = Student.query.filter_by(email=cleaned["email"]).first()
        if existing:
            return jsonify({"error": "A student with this email already exists."}), 409

    student.first_name = cleaned["first_name"]
    student.last_name = cleaned["last_name"]
    student.email = cleaned["email"]
    student.date_of_birth = cleaned["date_of_birth"]
    student.enrollment_status = cleaned["enrollment_status"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A student with this email already exists."}), 409

    return jsonify(student.to_dict()), 200


@students_bp.route("/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"error": "Student not found."}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully."}), 200
