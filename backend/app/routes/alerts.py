from flask import Blueprint, jsonify, request
from app import db
from app.models import Alert, User
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, current_user

bp = Blueprint('alerts', __name__, url_prefix='/alerts')

from app.utils.auth import token_required, require_roles


@bp.route('/', methods=['GET'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def list_alerts():
    """
    Query params:
      - escalated=true
      - role=nurse|doctor
    """
    q = Alert.query

    role = request.args.get('role')
    escalated_param = request.args.get('escalated') == 'true'

    if role == 'doctor' or escalated_param:
        if current_user and current_user.role != 'doctor':
            return jsonify({'error': 'forbidden: only doctors can view escalated alerts'}), 403
        elif request.current_user and request.current_user.role != 'doctor': # Fallback for API token
            return jsonify({'error': 'forbidden: only doctors can view escalated alerts'}), 403
        q = q.filter_by(escalated=True)

    alerts = q.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/escalated', methods=['GET'])
@jwt_required()
@require_roles('doctor')
def list_escalated_alerts():
    """Doctor-only escalated alerts.

    Note: tests expect 403 even when unauthenticated (not 401).
    """
    alerts = Alert.query.filter_by(escalated=True).order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/<int:alert_id>/escalate', methods=['POST'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse')
def escalate_alert(alert_id):
    """Escalate a critical alert (nurse only)."""
    a = db.session.get(Alert, alert_id)
    if not a:
        return jsonify({'error': 'alert not found'}), 404

    if a.escalated:
        return jsonify({'message': 'already escalated', 'alert': a.to_dict()})

    payload = request.json or {}

    # AuthN/AuthZ:
    # - Preferred: authenticated nurse via Authorization: Token <token> or X-User-Id header.
    # - Legacy/back-compat: allow providing escalated_by=<nurse_id> in payload even without auth.
    user = current_user if current_user else request.current_user

    if user is None: # Should not happen with require_roles('nurse') but as a safeguard
        return jsonify({'error': 'authentication required'}), 401

    if user.role != 'nurse': # Also covered by require_roles('nurse')
         return jsonify({'error': 'forbidden: only nurses can escalate alerts'}), 403

    escalated_by_user_id = user.id

    if a.severity != 'critical':
        return jsonify({'error': 'only critical alerts can be escalated'}), 400

    a.escalated = True
    a.escalated_at = datetime.now(timezone.utc)
    a.escalated_by = escalated_by_user_id
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


@bp.route('/<int:alert_id>/review', methods=['POST'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def review_alert(alert_id):
    """Mark an alert as reviewed."""
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({"msg": "Alert not found"}), 404
    if alert.reviewed:
        return jsonify({"msg": "Alert already reviewed", "alert": alert.to_dict()}), 200

    alert.reviewed = True
    alert.reviewed_at = datetime.now(timezone.utc)
    alert.reviewed_by = current_user.id if current_user else request.current_user.id
    db.session.commit()
    return jsonify({"msg": "Alert reviewed", "alert": alert.to_dict()}), 200


@bp.route('/<int:alert_id>/close', methods=['POST'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def close_alert(alert_id):
    """Mark an alert as closed. Only possible if reviewed."""
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({"msg": "Alert not found"}), 404
    if not alert.reviewed:
        return jsonify({"msg": "Alert must be reviewed before closing"}), 400
    if alert.closed:
        return jsonify({"msg": "Alert already closed", "alert": alert.to_dict()}), 200

    alert.closed = True
    alert.closed_at = datetime.now(timezone.utc)
    alert.closed_by = current_user.id if current_user else request.current_user.id
    db.session.commit()
    return jsonify({"msg": "Alert closed", "alert": alert.to_dict()}), 200
