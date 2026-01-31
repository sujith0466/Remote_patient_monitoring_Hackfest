from flask import Blueprint, jsonify
from app.models import User
from app import db

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])
