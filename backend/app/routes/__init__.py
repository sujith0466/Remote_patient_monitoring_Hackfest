def register_blueprints(app):
    from app.routes.users import bp as users_bp
    from app.routes.patients import bp as patients_bp
    from app.routes.alerts import bp as alerts_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(alerts_bp)
