from flask import Blueprint, request, jsonify
from app import db
from app.models import Patient, PatientVital, Alert
from app.utils.auth import require_roles
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')


@bp.route('/', methods=['GET'])
def list_patients():
    patients = Patient.query.all()
    return jsonify([p.to_dict() for p in patients])


@bp.route('/vitals', methods=['GET'])
def list_vitals():
    """Return recent vitals across all patients. Query params: ?limit=100 (default) or ?patient_id=<id>"""
    limit = min(int(request.args.get('limit', 100)), 1000)
    q = PatientVital.query.order_by(PatientVital.timestamp.desc())

    if request.args.get('patient_id'):
        try:
            pid = int(request.args.get('patient_id'))
            q = q.filter_by(patient_id=pid)
        except ValueError:
            return jsonify({'error': 'invalid patient_id'}), 400

    vitals = q.limit(limit).all()
    result = []
    for v in vitals:
        d = v.to_dict()
        d['patient_name'] = v.patient.name if v.patient else None
        result.append(d)

    return jsonify(result)


@bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404
    return jsonify(patient.to_dict())


@bp.route('/<int:patient_id>/vitals', methods=['GET'])
def get_patient_vitals(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404

    limit = min(int(request.args.get('limit', 100)), 1000)
    vitals = (
        PatientVital.query
        .filter_by(patient_id=patient_id)
        .order_by(PatientVital.timestamp.desc())
        .limit(limit)
        .all()
    )
    return jsonify([v.to_dict() for v in vitals])


@bp.route('/<int:patient_id>/vitals', methods=['POST'])
def submit_vitals(patient_id):
    """Accepts JSON: { heart_rate, temperature, spo2 } and creates alerts if needed"""
    payload = request.json or {}

    if not any(k in payload for k in ('heart_rate', 'temperature', 'spo2')):
        return jsonify({'error': 'at least one vital is required'}), 400

    # ----------------------------
    # Validators
    # ----------------------------
    def _parse_int(val, name, min_v, max_v):
        if val is None:
            return None
        iv = int(val)
        if iv < min_v or iv > max_v:
            raise ValueError(f"{name} must be between {min_v} and {max_v}")
        return iv

    def _parse_float(val, name, min_v, max_v):
        if val is None:
            return None
        fv = float(val)
        if fv < min_v or fv > max_v:
            raise ValueError(f"{name} must be between {min_v} and {max_v}")
        return fv

    try:
        hr = _parse_int(payload.get('heart_rate'), 'heart_rate', 20, 220)
        temp = _parse_float(payload.get('temperature'), 'temperature', 30.0, 45.0)
        spo2 = _parse_int(payload.get('spo2'), 'spo2', 50, 100)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404

    from app.utils.simulator import create_vital_and_alerts

    try:
        vital_dict, alerts_list = create_vital_and_alerts(
            patient.id,
            heart_rate=hr,
            temperature=temp,
            spo2=spo2
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'internal server error'}), 500

    return jsonify({
        'vital': vital_dict,
        'alerts_created': alerts_list
    }), 201


@bp.route('/<int:patient_id>', methods=['PATCH'])
@require_roles('nurse', 'doctor')
def update_patient(patient_id):
    """Update patient demographic/details."""
    payload = request.json or {}
    allowed = {'age', 'sex', 'room', 'weight_kg', 'notes'}

    if not any(k in payload for k in allowed):
        return jsonify({'error': 'no valid fields provided'}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404

    try:
        if 'age' in payload:
            age = payload.get('age')
            patient.age = int(age) if age is not None else None

        if 'sex' in payload:
            patient.sex = payload.get('sex')

        if 'room' in payload:
            patient.room = payload.get('room')

        if 'weight_kg' in payload:
            patient.weight_kg = float(payload.get('weight_kg')) if payload.get('weight_kg') is not None else None

        if 'notes' in payload:
            patient.notes = payload.get('notes')

        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'internal error'}), 500

    return jsonify(patient.to_dict())
