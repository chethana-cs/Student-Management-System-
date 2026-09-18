import pytest

from app import create_app, db
from app.config import TestConfig


@pytest.fixture
def app():
    """Create a fresh app instance with an in-memory database for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client — sends requests without running a real server."""
    return app.test_client()


def sample_student(**overrides):
    """Returns a valid student dict. Override any field via kwargs."""
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "date_of_birth": "2000-05-15",
        "enrollment_status": "active",
    }
    data.update(overrides)
    return data
