from flask import Blueprint, jsonify, request
from app.models import User
from app import db
import secrets

from app.utils.auth import get_current_user, token_required
from flask_jwt_extended import jwt_required, current_user

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@bp.route('/auth/login', methods=['POST'])
def legacy_token_login():
    """Simple demo login: POST { \"user_id\": <id> } returns { api_token } for that user.
    This is intentionally simple for demo purposes only (no password) and is kept
    for backward compatibility / Demo Mode."""
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
        return jsonify({'api_token': u.api_token, 'user': u.to_dict()})
    except Exception:
        return jsonify({'error': 'invalid user_id'}), 400


@bp.route('/me', methods=['GET'])
@jwt_required(optional=True) # Make JWT optional
@token_required # For API token compatibility
def me():
    """
    Return current user info.

    Supports both:
      - Legacy Token auth (Authorization: Token <token> / X-User-Id)
      - JWT Bearer auth (Authorization: Bearer <access>)
    """
    # Prefer JWT if present
    if current_user:
        return jsonify(current_user.to_dict())

    # Fallback to legacy token-based auth
    u = get_current_user()
    if not u:
        return jsonify({'error': 'not authenticated'}), 401
    return jsonify(u.to_dict())

