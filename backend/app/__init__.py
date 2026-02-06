from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager # Import JWTManager
import os
from pathlib import Path

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() # Initialize JWTManager

def create_app(config_class=None):
    # 🔑 CRITICAL FIX (already correct)
    app = Flask(__name__, instance_relative_config=True)

    # Load base config
    app.config.from_object(config_class or 'app.config.Config')

    # ----------------------------
    # FORCE DATABASE_URL OVERRIDE
    # ----------------------------
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # ✅ Flask-managed instance folder
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)

        # ✅ ABSOLUTE, RESOLVED PATH (Windows-safe)
        db_path = (instance_path / "dev.db").resolve()
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app) # Initialize JWT with the app

    # Configure JWT
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = app.config["JWT_ACCESS_EXPIRES_MIN"] * 60
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = app.config["JWT_REFRESH_EXPIRES_MIN"] * 60

    @jwt.user_identity_loader
    def user_identity_callback(user):
        return user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        from app.models import User
        return User.query.filter_by(id=identity).one_or_none()

    # Enable CORS
    from flask_cors import CORS
    # Get origins from env var, defaulting to common dev ports
    env_origins = os.getenv("CORS_ORIGINS")
    if env_origins:
        # If env var is set, split it by comma
        allowed_origins = [o.strip() for o in env_origins.split(",")]
    else:
        # If env var is not set, use both common dev ports as defaults
        allowed_origins = ["http://localhost:3000", "http://localhost:5173"]

    CORS(app, resources={r"/*": {"origins": allowed_origins}})

    # Register routes
    from app.routes import register_blueprints
    register_blueprints(app)

    @app.route("/")
    def index():
        return {"app": "CareWatch Backend", "status": "ok"}

    return app
