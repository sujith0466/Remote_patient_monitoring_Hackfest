import random
from datetime import datetime, timezone
from app import db
from app.models import Patient, PatientVital, Alert


def generate_random_vitals():
    """Return a dict with simulated heart_rate, temperature, spo2."""
    # Base normal ranges
    hr = random.randint(58, 100)
    temp = round(random.uniform(36.5, 37.5), 1)
    spo2 = random.randint(94, 99)

    # small chance to produce abnormal values
    if random.random() < 0.08:
        # critical temp bump
        temp = round(random.uniform(38.1, 39.5), 1)
    if random.random() < 0.06:
        spo2 = random.randint(85, 89)
    if random.random() < 0.07:
        hr = random.randint(45, 120)

    return {'heart_rate': hr, 'temperature': temp, 'spo2': spo2}


def create_vital_and_alerts(patient_id, heart_rate=None, temperature=None, spo2=None):
    """Create a PatientVital and rule-based Alerts according to project rules.

    Validation is performed on inputs; invalid values raise ValueError with explanatory message.

    Returns (vital_dict, [alert_dicts])
    """
    patient = db.session.get(Patient, patient_id)
    if not patient:
        raise ValueError('patient not found')

    # If values are None, generate random ones
    if heart_rate is None or temperature is None or spo2 is None:
        d = generate_random_vitals()
        heart_rate = heart_rate if heart_rate is not None else d['heart_rate']
        temperature = temperature if temperature is not None else d['temperature']
        spo2 = spo2 if spo2 is not None else d['spo2']

    # Validate types and ranges
    try:
        if heart_rate is not None:
            heart_rate = int(heart_rate)
            if heart_rate < 20 or heart_rate > 220:
                raise ValueError('heart_rate must be between 20 and 220')
        if temperature is not None:
            temperature = float(temperature)
            if temperature < 30.0 or temperature > 45.0:
                raise ValueError('temperature must be between 30.0 and 45.0')
        if spo2 is not None:
            spo2 = int(spo2)
            if spo2 < 50 or spo2 > 100:
                raise ValueError('spo2 must be between 50 and 100')
    except (TypeError, ValueError) as e:
        # Re-raise as ValueError with message
        raise ValueError(str(e))

    vital = PatientVital(patient_id=patient.id, heart_rate=heart_rate, temperature=temperature, spo2=spo2, timestamp=datetime.now(timezone.utc))
    db.session.add(vital)

    alerts_created = []

    # Temperature > 38.0 => critical
    if temperature is not None and temperature > 38.0:
        a = Alert(patient_id=patient.id, severity='critical', message=f'Temperature {temperature}°C — threshold exceeded')
        a.escalated = True # Auto-escalate critical alerts for demo
        a.escalated_at = datetime.now(timezone.utc)
        a.escalated_by = 1 # Assuming demo Nurse ID is 1 for auto-escalation
        db.session.add(a)
        alerts_created.append(a)

    # SpO2 < 90 => critical
    if spo2 is not None and spo2 < 90:
        a = Alert(patient_id=patient.id, severity='critical', message=f'SpO₂ {spo2}% — threshold exceeded')
        a.escalated = True # Auto-escalate critical alerts for demo
        a.escalated_at = datetime.now(timezone.utc)
        a.escalated_by = 1 # Assuming demo Nurse ID is 1 for auto-escalation
        db.session.add(a)
        alerts_created.append(a)

    # Heart rate < 60 or > 100 => warning
    if heart_rate is not None and (heart_rate < 60 or heart_rate > 100):
        a = Alert(patient_id=patient.id, severity='warning', message=f'Heart Rate {heart_rate} bpm — outside normal range')
        db.session.add(a)
        alerts_created.append(a)

    db.session.commit()

    return vital.to_dict(), [a.to_dict() for a in alerts_created]
