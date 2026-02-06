def register_blueprints(app):
    from app.routes.users import bp as users_bp
    from app.routes.patients import bp as patients_bp
    from app.routes.alerts import bp as alerts_bp
    from app.routes.auth import auth_bp # Import the auth blueprint
    from app.routes.notes import notes_bp # Import the notes blueprint
    from app.routes.analytics import analytics_bp # Import the analytics blueprint

    app.register_blueprint(users_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(auth_bp) # Register the auth blueprint
    app.register_blueprint(notes_bp) # Register the notes blueprint
    app.register_blueprint(analytics_bp) # Register the analytics blueprint
