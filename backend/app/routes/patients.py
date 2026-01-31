from flask import Blueprint, request, jsonify
from app import db
from app.models import Patient, PatientVital, Alert
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')


@bp.route('/', methods=['GET'])
def list_patients():
    patients = Patient.query.all()
    return jsonify([p.to_dict() for p in patients])


@bp.route('/vitals', methods=['GET'])
def list_vitals():
    """Return recent vitals across all patients. Query params: ?limit=100 (default) or ?patient_id=<id> to filter."""
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


@bp.route('/<int:patient_id>/vitals', methods=['GET'])
def get_patient_vitals(patient_id):
    """Return recent vitals for a specific patient."""
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404
    limit = min(int(request.args.get('limit', 100)), 1000)
    vitals = PatientVital.query.filter_by(patient_id=patient_id).order_by(PatientVital.timestamp.desc()).limit(limit).all()
    return jsonify([v.to_dict() for v in vitals])


@bp.route('/<int:patient_id>/vitals', methods=['POST'])
def submit_vitals(patient_id):
    """Accepts JSON: { "heart_rate": int, "temperature": float, "spo2": int }
    Creates a PatientVital record and generates rule-based Alerts if thresholds exceeded.

    Validation rules:
      - At least one of heart_rate, temperature, or spo2 must be provided
      - heart_rate: integer, 20-220
      - temperature: float, 30.0-45.0
      - spo2: integer, 50-100
    """
    payload = request.json or {}

    if not any(k in payload for k in ('heart_rate', 'temperature', 'spo2')):
        return jsonify({'error': 'at least one of heart_rate, temperature, or spo2 is required'}), 400

    # parse and validate inputs
    hr = payload.get('heart_rate')
    temp = payload.get('temperature')
    spo2 = payload.get('spo2')

    def _parse_int(val, name, min_v, max_v):
        if val is None:
            return None
        try:
            iv = int(val)
        except Exception:
            raise ValueError(f"{name} must be an integer")
        if iv < min_v or iv > max_v:
            raise ValueError(f"{name} must be between {min_v} and {max_v}")
        return iv

    def _parse_float(val, name, min_v, max_v):
        if val is None:
            return None
        try:
            fv = float(val)
        except Exception:
            raise ValueError(f"{name} must be a number")
        if fv < min_v or fv > max_v:
            raise ValueError(f"{name} must be between {min_v} and {max_v}")
        return fv

    try:
        hr = _parse_int(hr, 'heart_rate', 20, 220)
        temp = _parse_float(temp, 'temperature', 30.0, 45.0)
        spo2 = _parse_int(spo2, 'spo2', 50, 100)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404

    def _parse_float(val, name, min_v, max_v):
        if val is None:
            return None
        try:
            fv = float(val)
        except Exception:
            raise ValueError(f"{name} must be a number")
        if fv < min_v or fv > max_v:
            raise ValueError(f"{name} must be between {min_v} and {max_v}")
        return fv

    try:
        hr = _parse_int(hr, 'heart_rate', 20, 220)
        temp = _parse_float(temp, 'temperature', 30.0, 45.0)
        spo2 = _parse_int(spo2, 'spo2', 50, 100)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'error': 'patient not found'}), 404

    # Delegate to simulator helper so the logic is consistent with demo generator
    from app.utils.simulator import create_vital_and_alerts

    try:
        vital_dict, alerts_list = create_vital_and_alerts(patient.id, heart_rate=hr, temperature=temp, spo2=spo2)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Unexpected error
        return jsonify({'error': 'internal server error'}), 500

    return jsonify({
        'vital': vital_dict,
        'alerts_created': alerts_list
    }), 201
