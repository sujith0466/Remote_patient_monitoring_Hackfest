import smtplib
from email.message import EmailMessage
from flask import current_app
import traceback


def send_escalation_email(app, alert_dict):
    """Send escalation email inside the provided Flask app context.

    alert_dict should be a mapping with keys: id, patient_id, severity, message, escalated_by, escalated_at
    """
    with app.app_context():
        cfg = current_app.config
        recipients = cfg.get('ALERT_EMAIL_RECIPIENTS', []) or []
        if not recipients:
            current_app.logger.info('No ALERT_EMAIL_RECIPIENTS configured; skipping escalation email')
            return False

        subject = f"[CareWatch] Escalated Alert — Patient {alert_dict.get('patient_id')} (#{alert_dict.get('id')})"
        body = f"""An alert has been escalated in CareWatch.

Alert ID: {alert_dict.get('id')}
Patient ID: {alert_dict.get('patient_id')}
Severity: {alert_dict.get('severity')}
Message: {alert_dict.get('message')}
Escalated by (user id): {alert_dict.get('escalated_by')}
Escalated at: {alert_dict.get('escalated_at')}

This message was sent by the CareWatch notification system (rule-based alerts only).
"""
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = cfg.get('EMAIL_FROM') or 'carewatch@example.com'
        msg['To'] = ', '.join(recipients)
        msg.set_content(body)

        try:
            server = smtplib.SMTP(cfg.get('SMTP_SERVER'), cfg.get('SMTP_PORT') or 587, timeout=10)
            server.starttls()
            username = cfg.get('SMTP_USERNAME')
            password = cfg.get('SMTP_PASSWORD')
            if username:
                server.login(username, password)
            server.send_message(msg)
            server.quit()
            current_app.logger.info(f"Escalation email sent for alert {alert_dict.get('id')} to {recipients}")
            return True
        except Exception as e:
            current_app.logger.exception('Failed to send escalation email: %s', e)
            current_app.logger.debug(traceback.format_exc())
            return False
