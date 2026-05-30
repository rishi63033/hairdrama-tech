# Main Flask app setup
# Took me a while to figure out the app factory pattern but it's
# much cleaner than having everything in one file

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Flask secret key - needed for session signing
    # make sure this is set in .env or Railway env vars before going live
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-dev-secret")

    # CORS setup - had to add both localhost and the Vercel URL here
    # otherwise the frontend kept getting blocked in production
    CORS(
        app,
        origins=[
            os.getenv("FRONTEND_URL", "http://localhost:3000"),
            "https://hairdrama-tech.vercel.app",  # Update with your Vercel URL
        ],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # Register route blueprints - each file handles its own group of endpoints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Simple health check endpoint - Railway pings this to know the app is up
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Task Manager API is running"}, 200

    return app
