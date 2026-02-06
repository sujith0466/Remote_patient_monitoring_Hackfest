from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import Note, Patient, User
from app.utils.auth import token_required, require_roles
from datetime import datetime, timezone

notes_bp = Blueprint('notes', __name__, url_prefix='/patients/<int:patient_id>/notes')

@notes_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def get_patient_notes(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    notes = Note.query.filter_by(patient_id=patient_id).order_by(Note.timestamp.desc()).all()
    return jsonify([note.to_dict() for note in notes]), 200

@notes_bp.route('/', methods=['POST'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def add_patient_note(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"msg": "Note content is required"}), 400

    user_id = current_user.id if current_user else request.current_user.id

    note = Note(patient_id=patient_id, user_id=user_id, content=content)
    db.session.add(note)
    db.session.commit()

    return jsonify(note.to_dict()), 201

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def delete_patient_note(patient_id, note_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    note = Note.query.filter_by(id=note_id, patient_id=patient_id).first()
    if not note:
        return jsonify({"msg": "Note not found"}), 404

    # Only the user who created the note or an admin (if we had one) can delete it
    user_id = current_user.id if current_user else request.current_user.id
    if note.user_id != user_id:
        return jsonify({"msg": "Forbidden: You can only delete your own notes"}), 403

    db.session.delete(note)
    db.session.commit()

    return jsonify({"msg": "Note deleted successfully"}), 200