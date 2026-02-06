from functools import wraps
from flask import request, g, jsonify
from app import db
from app.models import User
import re
from flask_jwt_extended import jwt_required, current_user


def _get_token_from_header():
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    m = re.match(r'^Token\s+(.+)$', auth)
    if m:
        return m.group(1)
    return None


def get_current_user():
    """
    Retrieves user from legacy API token or X-User-Id header.
    Sets g.current_user and request.current_user if found.
    """
    # 1) Token in Authorization header
    token = _get_token_from_header()
    if token:
        u = User.query.filter_by(api_token=token).first()
        if u:
            g.current_user = u
            request.current_user = u # For consistency with JWT
            return u

    # 2) X-User-Id header (dev/back-compat)
    uid = request.headers.get('X-User-Id')
    if uid:
        try:
            u = db.session.get(User, int(uid))
            if u:
                g.current_user = u
                request.current_user = u # For consistency with JWT
                return u
        except Exception:
            pass

    # not authenticated
    g.current_user = None
    request.current_user = None
    return None

def token_required(f):
    """
    Decorator for legacy API token authentication.
    If a valid API token is found, sets request.current_user.
    Does not prevent further execution if no token is found,
    allowing combination with jwt_required(optional=True).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only attempt API token auth if JWT hasn't already authenticated a user
        if not current_user:
            get_current_user() # This will set request.current_user if token found
        return f(*args, **kwargs)
    return decorated_function


def require_roles(*roles):
    """
    Role enforcement decorator for both JWT and API token authentication.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = current_user # Try JWT authenticated user first
            if not user:
                user = request.current_user # Fallback to API token authenticated user

            if not user:
                return jsonify({'error': 'authentication required'}), 401
            if user.role not in roles:
                return jsonify({'error': 'forbidden: insufficient role'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

