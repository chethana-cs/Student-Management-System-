from flask import Blueprint

students_bp = Blueprint("students", __name__)

from app.routes import students  # noqa: E402, F401 — register route handlers
