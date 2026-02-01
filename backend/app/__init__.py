from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from pathlib import Path

db = SQLAlchemy()
migrate = Migrate()


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

    # Enable CORS
    from flask_cors import CORS
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    CORS(app, resources={r"/*": {"origins": [o.strip() for o in origins.split(",")]}})

    # Register routes
    from app.routes import register_blueprints
    register_blueprints(app)

    @app.route("/")
    def index():
        return {"app": "CareWatch Backend", "status": "ok"}

    return app
