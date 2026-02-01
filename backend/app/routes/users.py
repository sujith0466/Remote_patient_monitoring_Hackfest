from flask import Blueprint, jsonify, request
from app.models import User
from app import db
import secrets

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@bp.route('/auth/login', methods=['POST'])
def login():
    """Simple demo login: POST { "user_id": <id> } returns { api_token } for that user.
    This is intentionally simple for demo purposes only (no password)."""
    payload = request.json or {}
    user_id = payload.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    try:
        u = db.session.get(User, int(user_id))
        if not u:
            return jsonify({'error': 'user not found'}), 404
        if not u.api_token:
            u.api_token = secrets.token_urlsafe(24)
            db.session.commit()
        return jsonify({'api_token': u.api_token})
    except Exception:
        return jsonify({'error': 'invalid user_id'}), 400


@bp.route('/me', methods=['GET'])
def me():
    """Return current user info when authenticated via Authorization: Token <token> or X-User-Id header"""
    from app.utils.auth import get_current_user
    u = get_current_user()
    if not u:
        return jsonify({'error': 'not authenticated'}), 401
    return jsonify(u.to_dict())
