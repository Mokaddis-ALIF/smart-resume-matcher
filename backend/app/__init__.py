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
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH

    # Enable CORS so the React frontend can call the API
    CORS(app)

    # Set up MongoDB connection
    mongo_client = MongoClient(Config.MONGO_URI)
    db = mongo_client[Config.DB_NAME]

    # Ensure uploads folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Seed skill taxonomy if empty
    from app.services.skill_taxonomy import seed_taxonomy
    seed_taxonomy(db)

    # Register route blueprints
    from app.routes.health import health_bp
    from app.routes.jobs import jobs_bp
    from app.routes.resumes import resumes_bp
    from app.routes.evaluation import evaluation_bp
    from app.routes.docs import docs_bp
    from app.routes.taxonomy import taxonomy_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(taxonomy_bp)

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(413)
    def file_too_large(e):
        return {"error": "File too large. Maximum size is 16MB."}, 413

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    return app
