from app.models import PatientVital, Alert
from datetime import datetime, timedelta, timezone
from sqlalchemy import desc

def calculate_risk_score(patient_id):
    """
    Calculates a simple risk score for a patient based on recent vitals and active alerts.
    - Recent critical alerts add high risk.
    - Recent warning alerts add medium risk.
    - Abnormal vital signs (even if not yet an alert) add low risk.
    - Lower SpO2, higher temperature, and very abnormal heart rates contribute more.
    """
    score = 0
    now = datetime.now(timezone.utc)

    # 1. Alerts contribution
    # Get active (non-closed) alerts for the last 24 hours
    recent_alerts = Alert.query.filter(
        Alert.patient_id == patient_id,
        Alert.closed == False,
        Alert.created_at >= (now - timedelta(hours=24))
    ).all()

    for alert in recent_alerts:
        if alert.severity == 'critical':
            score += 10 # High impact
        elif alert.severity == 'warning':
            score += 5  # Medium impact

    # 2. Vitals contribution (most recent only for quick assessment)
    latest_vital = PatientVital.query.filter_by(patient_id=patient_id).order_by(desc(PatientVital.timestamp)).first()

    if latest_vital:
        hr = latest_vital.heart_rate
        temp = latest_vital.temperature
        spo2 = latest_vital.spo2

        # SpO2
        if spo2 < 90: score += 7 # Critical threshold
        elif spo2 < 94: score += 3 # Warning range

        # Temperature
        if temp > 38.0: score += 7 # Critical threshold
        elif temp > 37.5: score += 3 # Warning range

        # Heart Rate
        if hr < 50 or hr > 110: score += 5 # High warning
        elif hr < 60 or hr > 100: score += 2 # Mild warning

    # Cap score at a reasonable max if needed, or normalize later
    return min(score, 20) # Max risk score of 20 for simplicity


def get_vital_trends(patient_id, vital_type, hours=24, interval_minutes=60):
    """
    Retrieves a trend for a specific vital type (e.g., 'heart_rate', 'temperature', 'spo2')
    over a given number of hours, averaged by interval_minutes.
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)

    raw_vitals = PatientVital.query.filter(
        PatientVital.patient_id == patient_id,
        PatientVital.timestamp >= start_time,
        PatientVital.timestamp <= end_time
    ).order_by(PatientVital.timestamp).all()

    if not raw_vitals:
        return []

    trends = []
    current_interval_start = start_time
    while current_interval_start < end_time:
        interval_end = current_interval_start + timedelta(minutes=interval_minutes)
        
        vitals_in_interval = [
            getattr(v, vital_type) for v in raw_vitals
            if v.timestamp >= current_interval_start and v.timestamp < interval_end and getattr(v, vital_type) is not None
        ]

        if vitals_in_interval:
            avg_value = sum(vitals_in_interval) / len(vitals_in_interval)
            trends.append({
                'timestamp': interval_end.isoformat(),
                'value': round(avg_value, 1)
            })
        else:
            # If no data in interval, use the last known value or None
            if trends:
                trends.append({
                    'timestamp': interval_end.isoformat(),
                    'value': trends[-1]['value'] # Carry forward last known value
                })
            else:
                trends.append({
                    'timestamp': interval_end.isoformat(),
                    'value': None
                })
        
        current_interval_start = interval_end

    return trends