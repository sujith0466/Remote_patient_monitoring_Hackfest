from functools import wraps
from flask import request, g, jsonify
from app import db
from app.models import User
import re


def _get_token_from_header():
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    m = re.match(r'^Token\s+(.+)$', auth)
    if m:
        return m.group(1)
    return None


def get_current_user():
    # 1) Token in Authorization header
    token = _get_token_from_header()
    if token:
        u = User.query.filter_by(api_token=token).first()
        if u:
            g.current_user = u
            return u

    # 2) X-User-Id header (dev/back-compat)
    uid = request.headers.get('X-User-Id')
    if uid:
        try:
            u = db.session.get(User, int(uid))
            if u:
                g.current_user = u
                return u
        except Exception:
            pass

    # not authenticated
    g.current_user = None
    return None


def require_roles(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'authentication required'}), 401
            if user.role not in roles:
                return jsonify({'error': 'forbidden: insufficient role'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
