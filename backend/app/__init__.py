from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)

    from app.routes import students_bp
    app.register_blueprint(students_bp, url_prefix="/students")

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    with app.app_context():
        from app import models  # noqa: F401 — ensure models are registered
        db.create_all()

    return app
