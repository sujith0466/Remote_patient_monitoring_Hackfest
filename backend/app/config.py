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
