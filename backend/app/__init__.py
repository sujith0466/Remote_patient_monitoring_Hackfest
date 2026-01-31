from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class or 'app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS for local frontend during development
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    # register routes
    from app.routes import register_blueprints
    register_blueprints(app)

    @app.route('/')
    def index():
        return {'app': 'CareWatch Backend', 'status': 'ok'}

    return app
