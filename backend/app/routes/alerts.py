from flask import Blueprint, jsonify, request
from app import db
from app.models import Alert, User
from datetime import datetime, timezone

bp = Blueprint('alerts', __name__, url_prefix='/alerts')


def _resolve_request_role():
    """Resolve role from headers or query params or user id lookup.

    Priority:
      1. X-User-Id header or user_id query param -> lookup User in DB
      2. X-User-Role header or role query param
      returns role string or None
    """
    uid = request.headers.get('X-User-Id') or request.args.get('user_id')
    if uid:
        try:
            u = db.session.get(User, int(uid))
            if u:
                return u.role
        except Exception:
            pass
    role = request.headers.get('X-User-Role') or request.args.get('role')
    return role


@bp.route('/', methods=['GET'])
def list_alerts():
    """List alerts.

    Query params:
      - escalated=true  -> returns only escalated alerts (backwards compatible)
      - role=nurse|doctor -> if role=doctor returns only escalated alerts (doctors see escalated alerts only); role=nurse returns all alerts
    """
    q = Alert.query

    # Determine requester role from headers/query/user id (basic, no auth)
    requester_role = _resolve_request_role()

    role = request.args.get('role')
    escalated_param = request.args.get('escalated') == 'true'

    if role == 'doctor' or escalated_param:
        # Only doctors are allowed to request escalated alerts
        if requester_role != 'doctor':
            return jsonify({'error': 'forbidden: only doctors can view escalated alerts'}), 403
        q = q.filter_by(escalated=True)

    alerts = q.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/escalated', methods=['GET'])
def list_escalated_alerts():
    """Return only escalated alerts (for doctors).

    Basic role check (no auth): require the request to indicate a doctor role via header `X-User-Role: doctor` or `X-User-Id` that maps to a user with role 'doctor'.
    """
    role = _resolve_request_role()
    if role != 'doctor':
        return jsonify({'error': 'forbidden: only doctors can view escalated alerts'}), 403

    alerts = Alert.query.filter_by(escalated=True).order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@bp.route('/<int:alert_id>/escalate', methods=['POST'])
def escalate_alert(alert_id):
    """Mark a critical alert as escalated by a nurse. Expects JSON { "escalated_by": <user_id> }.

    Only alerts with severity 'critical' can be escalated. Escalation marks the alert so doctors can see it.
    """
    a = db.session.get(Alert, alert_id)
    if not a:
        return jsonify({'error': 'alert not found'}), 404

    if a.escalated:
        return jsonify({'message': 'already escalated', 'alert': a.to_dict()})

    if a.severity != 'critical':
        return jsonify({'error': 'only critical alerts can be escalated'}), 400

    payload = request.json or {}
    escalated_by = payload.get('escalated_by')
    header_role = request.headers.get('X-User-Role')
    header_user_id = request.headers.get('X-User-Id')

    # Accept escalation if either:
    #  - escalated_by is provided and maps to a user with role 'nurse', OR
    #  - header 'X-User-Role' == 'nurse' (optional X-User-Id header can be used as escalated_by)
    if escalated_by:
        try:
            nurse = db.session.get(User, int(escalated_by))
            if not nurse or nurse.role != 'nurse':
                return jsonify({'error': 'forbidden: only nurses can escalate alerts'}), 403
        except Exception:
            return jsonify({'error': 'invalid escalated_by id'}), 400
    else:
        if header_role == 'nurse':
            # allow anonymous nurse escalation; prefer header user id if provided
            if header_user_id:
                try:
                    nu = db.session.get(User, int(header_user_id))
                    if nu and nu.role == 'nurse':
                        escalated_by = int(header_user_id)
                    else:
                        escalated_by = None
                except Exception:
                    escalated_by = None
            else:
                escalated_by = None
        else:
            return jsonify({'error': 'escalated_by (nurse id) is required or provide X-User-Role: nurse header'}), 400

    a.escalated = True
    a.escalated_at = datetime.now(timezone.utc)
    a.escalated_by = escalated_by

    db.session.commit()

    # send notification to doctors (background thread so request isn't delayed)
    try:
        from threading import Thread
        from flask import current_app
        from app.utils.mailer import send_escalation_email

        # send minimal alert dict to mailer in background
        app_obj = current_app._get_current_object()
        alert_payload = a.to_dict()
        Thread(target=send_escalation_email, args=(app_obj, alert_payload), daemon=True).start()
    except Exception:
        # log but do not fail the request
        try:
            current_app.logger.exception('Failed to start email notification thread')
        except Exception:
            pass

    return jsonify({'message': 'escalated', 'alert': a.to_dict()})
