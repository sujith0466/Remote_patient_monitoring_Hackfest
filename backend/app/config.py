import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@localhost/carewatch')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SMTP / Email settings (used for escalation notifications)
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    ALERT_EMAIL_RECIPIENTS = [e.strip() for e in os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',') if e.strip()]

    # JWT settings (used for email/password auth with access + refresh tokens)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY', 'dev-secret-change-me'))
    # Expiry in minutes
    JWT_ACCESS_EXPIRES_MIN = int(os.getenv('JWT_ACCESS_EXPIRES_MIN', '15'))          # 15 minutes
    JWT_REFRESH_EXPIRES_MIN = int(os.getenv('JWT_REFRESH_EXPIRES_MIN', str(7 * 24 * 60)))  # 7 days
