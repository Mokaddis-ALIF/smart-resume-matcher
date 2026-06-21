import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config

# MongoDB client — shared across the app
mongo_client = None
db = None


def create_app():
    """Create and configure the Flask application."""
    global mongo_client, db

    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS so the React frontend can call the API
    CORS(app)

    # Set up MongoDB connection
    mongo_client = MongoClient(Config.MONGO_URI)
    db = mongo_client[Config.DB_NAME]

    # Ensure uploads folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Register route blueprints
    from app.routes.health import health_bp
    from app.routes.jobs import jobs_bp
    from app.routes.resumes import resumes_bp
    from app.routes.evaluation import evaluation_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(evaluation_bp)

    return app
