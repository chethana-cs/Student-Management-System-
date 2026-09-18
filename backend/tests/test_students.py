"""Tests for Student CRUD API endpoints."""

from tests.conftest import sample_student


# --- POST /students ---


class TestCreateStudent:
    def test_create_student_success(self, client):
        """Successful creation returns 201 with all fields."""
        response = client.post("/students", json=sample_student())

        assert response.status_code == 201
        data = response.get_json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Doe"
        assert data["email"] == "jane@example.com"
        assert data["date_of_birth"] == "2000-05-15"
        assert data["enrollment_status"] == "active"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_missing_fields(self, client):
        """Missing required fields returns 400 with details."""
        response = client.post("/students", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert "details" in data
        assert len(data["details"]) == 5  # all 5 fields missing

    def test_create_empty_names(self, client):
        """Whitespace-only names are rejected."""
        response = client.post("/students", json=sample_student(
            first_name="   ", last_name=""
        ))

        assert response.status_code == 400
        details = response.get_json()["details"]
        assert any("first_name" in d for d in details)
        assert any("last_name" in d for d in details)

    def test_create_invalid_email(self, client):
        """Malformed email returns 400."""
        response = client.post("/students", json=sample_student(
            email="not-an-email"
        ))

        assert response.status_code == 400
        details = response.get_json()["details"]
        assert any("email" in d for d in details)

    def test_create_duplicate_email(self, client):
        """Duplicate email returns 409."""
        client.post("/students", json=sample_student())
        response = client.post("/students", json=sample_student(
            first_name="John"
        ))

        assert response.status_code == 409
        assert "already exists" in response.get_json()["error"]

    def test_create_future_date_of_birth(self, client):
        """Future date_of_birth returns 400."""
        response = client.post("/students", json=sample_student(
            date_of_birth="2099-01-01"
        ))

        assert response.status_code == 400
        details = response.get_json()["details"]
        assert any("future" in d for d in details)

    def test_create_invalid_date_format(self, client):
        """Non-YYYY-MM-DD date returns 400."""
        response = client.post("/students", json=sample_student(
            date_of_birth="15/05/2000"
        ))

        assert response.status_code == 400
        details = response.get_json()["details"]
        assert any("date_of_birth" in d for d in details)

    def test_create_invalid_enrollment_status(self, client):
        """Invalid enrollment_status returns 400."""
        response = client.post("/students", json=sample_student(
            enrollment_status="expelled"
        ))

        assert response.status_code == 400
        details = response.get_json()["details"]
        assert any("enrollment_status" in d for d in details)

    def test_create_invalid_json_body(self, client):
        """Non-JSON body returns 400."""
        response = client.post(
            "/students",
            data="not json",
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "JSON" in response.get_json()["error"]

    def test_create_email_normalized_to_lowercase(self, client):
        """Email is stored as lowercase."""
        response = client.post("/students", json=sample_student(
            email="Jane.Doe@EXAMPLE.COM"
        ))

        assert response.status_code == 201
        assert response.get_json()["email"] == "jane.doe@example.com"


# --- GET /students/{id} ---


class TestGetStudent:
    def test_get_student_success(self, client):
        """Get existing student returns 200."""
        create_resp = client.post("/students", json=sample_student())
        student_id = create_resp.get_json()["id"]

        response = client.get(f"/students/{student_id}")

        assert response.status_code == 200
        assert response.get_json()["id"] == student_id

    def test_get_student_not_found(self, client):
        """Get non-existent student returns 404."""
        response = client.get("/students/999")

        assert response.status_code == 404
        assert "not found" in response.get_json()["error"].lower()


# --- PUT /students/{id} ---


class TestUpdateStudent:
    def test_update_student_success(self, client):
        """Successful update returns 200 with changed fields."""
        create_resp = client.post("/students", json=sample_student())
        student_id = create_resp.get_json()["id"]

        response = client.put(f"/students/{student_id}", json=sample_student(
            first_name="Janet", enrollment_status="graduated"
        ))

        assert response.status_code == 200
        data = response.get_json()
        assert data["first_name"] == "Janet"
        assert data["enrollment_status"] == "graduated"

    def test_update_student_not_found(self, client):
        """Update non-existent student returns 404."""
        response = client.put("/students/999", json=sample_student())

        assert response.status_code == 404

    def test_update_duplicate_email(self, client):
        """Changing email to an existing one returns 409."""
        client.post("/students", json=sample_student(email="first@test.com"))
        create_resp = client.post("/students", json=sample_student(email="second@test.com"))
        student_id = create_resp.get_json()["id"]

        response = client.put(f"/students/{student_id}", json=sample_student(
            email="first@test.com"
        ))

        assert response.status_code == 409

    def test_update_same_email_no_conflict(self, client):
        """Keeping the same email on update should not trigger 409."""
        create_resp = client.post("/students", json=sample_student())
        student_id = create_resp.get_json()["id"]

        response = client.put(f"/students/{student_id}", json=sample_student())

        assert response.status_code == 200


# --- DELETE /students/{id} ---


class TestDeleteStudent:
    def test_delete_student_success(self, client):
        """Delete returns 200, then re-fetch returns 404."""
        create_resp = client.post("/students", json=sample_student())
        student_id = create_resp.get_json()["id"]

        response = client.delete(f"/students/{student_id}")
        assert response.status_code == 200

        # Verify it's actually gone
        get_resp = client.get(f"/students/{student_id}")
        assert get_resp.status_code == 404

    def test_delete_student_not_found(self, client):
        """Delete non-existent student returns 404."""
        response = client.delete("/students/999")

        assert response.status_code == 404


# --- GET /students (list, pagination, filtering) ---


class TestListStudents:
    def _seed_students(self, client, count=5):
        """Helper to create multiple students."""
        ids = []
        for i in range(count):
            resp = client.post("/students", json=sample_student(
                first_name=f"Student{i}",
                email=f"student{i}@test.com",
                enrollment_status="active" if i < 3 else "graduated",
            ))
            ids.append(resp.get_json()["id"])
        return ids

    def test_list_empty(self, client):
        """Empty database returns empty list with total 0."""
        response = client.get("/students")

        assert response.status_code == 200
        data = response.get_json()
        assert data["students"] == []
        assert data["total"] == 0

    def test_list_pagination(self, client):
        """Pagination returns correct page metadata."""
        self._seed_students(client, 5)

        response = client.get("/students?page=1&per_page=2")

        data = response.get_json()
        assert len(data["students"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["pages"] == 3

    def test_list_filter_by_status(self, client):
        """Filtering by enrollment_status returns only matching students."""
        self._seed_students(client, 5)  # 3 active, 2 graduated

        response = client.get("/students?enrollment_status=active")

        data = response.get_json()
        assert data["total"] == 3
        assert all(s["enrollment_status"] == "active" for s in data["students"])

    def test_list_filter_and_paginate(self, client):
        """Filtering and pagination work together."""
        self._seed_students(client, 5)  # 3 active, 2 graduated

        response = client.get("/students?enrollment_status=active&page=1&per_page=2")

        data = response.get_json()
        assert len(data["students"]) == 2
        assert data["total"] == 3
        assert data["pages"] == 2

    def test_list_invalid_page(self, client):
        """Non-integer page returns 400."""
        response = client.get("/students?page=abc")

        assert response.status_code == 400

    def test_list_invalid_status(self, client):
        """Invalid enrollment_status filter returns 400."""
        response = client.get("/students?enrollment_status=expelled")

        assert response.status_code == 400
