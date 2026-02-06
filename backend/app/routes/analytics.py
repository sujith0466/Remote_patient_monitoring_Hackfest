from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.auth import token_required, require_roles
from app import db
from app.models import Patient
from app.utils.risk_assessment import calculate_risk_score, get_vital_trends
from sqlalchemy import desc

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/patients/<int:patient_id>/risk', methods=['GET'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def get_patient_risk_score(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    risk_score = calculate_risk_score(patient_id)
    return jsonify({"patient_id": patient_id, "risk_score": risk_score}), 200


@analytics_bp.route('/patients/<int:patient_id>/trends/<string:vital_type>', methods=['GET'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def get_patient_vital_trends(patient_id, vital_type):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    if vital_type not in ['heart_rate', 'temperature', 'spo2']:
        return jsonify({"msg": "Invalid vital type. Must be heart_rate, temperature, or spo2"}), 400

    hours = int(request.args.get('hours', 24))
    interval_minutes = int(request.args.get('interval', 60))

    trends = get_vital_trends(patient_id, vital_type, hours, interval_minutes)
    return jsonify({
        "patient_id": patient_id,
        "vital_type": vital_type,
        "trends": trends
    }), 200

@analytics_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required(optional=True)
@token_required
@require_roles('nurse', 'doctor')
def get_dashboard_summary():
    """
    Provides a summary for the dashboard, e.g., total patients, patients at risk.
    """
    total_patients = Patient.query.count()
    
    # This is a simplified example. In a real app, this would involve more complex
    # logic, potentially caching risk scores or having a dedicated 'patients_at_risk' table.
    patients = Patient.query.all()
    patients_at_risk_count = 0
    patient_risk_list = []
    
    for patient in patients:
        risk_score = calculate_risk_score(patient.id)
        if risk_score > 5: # Arbitrary threshold for 'at risk'
            patients_at_risk_count += 1
            patient_risk_list.append({
                "patient_id": patient.id,
                "name": patient.name,
                "risk_score": risk_score
            })
            
    return jsonify({
        "total_patients": total_patients,
        "patients_at_risk_count": patients_at_risk_count,
        "patients_at_risk_details": patient_risk_list
    }), 200
