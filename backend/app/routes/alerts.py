from flask import Blueprint, jsonify, request
from app import db
from app.models import Alert, User
from datetime import datetime, timezone

bp = Blueprint('alerts', __name__, url_prefix='/alerts')

from app.utils.auth import get_current_user, require_roles


def _resolve_request_role():
    """Legacy helper (kept for backward compat)."""
    user = get_current_user()
    if user:
        return user.role
    return request.headers.get('X-User-Role') or request.args.get('role')


@bp.route('/', methods=['GET'])
def list_alerts():
    """
    Query params:
      - escalated=true
      - role=nurse|doctor
    """
    q = Alert.query
    requester_role = _resolve_request_role()

    role = request.args.get('role')
    escalated_param = request.args.get('escalated') == 'true'

    if role == 'doctor' or escalated_param:
        if requester_role != 'doctor':
            return jsonify({'error': 'forbidden: only doctors can view escalated alerts'}), 403
        q = q.filter_by(escalated=True)

    alerts = q.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/escalated', methods=['GET'])
@require_roles('doctor')
def list_escalated_alerts():
    """Doctor-only escalated alerts."""
    alerts = Alert.query.filter_by(escalated=True).order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/<int:alert_id>/escalate', methods=['POST'])
@require_roles('nurse')
def escalate_alert(alert_id):
    """Escalate a critical alert (nurse only)."""
    a = db.session.get(Alert, alert_id)
    if not a:
        return jsonify({'error': 'alert not found'}), 404

    if a.escalated:
        return jsonify({'message': 'already escalated', 'alert': a.to_dict()})

    if a.severity != 'critical':
        return jsonify({'error': 'only critical alerts can be escalated'}), 400

    payload = request.json or {}
    escalated_by = payload.get('escalated_by')

    if escalated_by:
        try:
            nurse = db.session.get(User, int(escalated_by))
            if not nurse or nurse.role != 'nurse':
                return jsonify({'error': 'forbidden: only nurses can escalate alerts'}), 403
        except Exception:
            return jsonify({'error': 'invalid escalated_by id'}), 400
    else:
        user = get_current_user()
        escalated_by = user.id

    a.escalated = True
    a.escalated_at = datetime.now(timezone.utc)
    a.escalated_by = escalated_by
    db.session.commit()

    # background notification
    try:
        from threading import Thread
        from flask import current_app
        from app.utils.mailer import send_escalation_email

        app_obj = current_app._get_current_object()
        Thread(
            target=send_escalation_email,
            args=(app_obj, a.to_dict()),
            daemon=True
        ).start()
    except Exception:
        pass

    return jsonify({'message': 'escalated', 'alert': a.to_dict()})
