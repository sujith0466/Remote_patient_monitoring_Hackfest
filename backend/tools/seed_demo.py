"""
Seed demo data into the CareWatch backend (users, patients, vitals, alerts).

Run with the backend virtualenv python, from the `backend` directory:

  .venv\Scripts\python tools\seed_demo.py

Options:
  --force  : delete existing demo users/patients created by this script before seeding
"""
import argparse
from datetime import datetime, timezone

from app import create_app, db
from app.models import User, Patient, PatientVital, Alert
from app.utils.simulator import create_vital_and_alerts


def seed(force=False):
    app = create_app()
    with app.app_context():
        # Simple marker to find demo records: names used below
        demo_nurse_name = 'Demo Nurse'
        demo_doctor_name = 'Demo Doctor'

        if force:
            # remove any existing demo users/patients/alerts/vitals with those names
            users_to_remove = User.query.filter(User.name.in_([demo_nurse_name, demo_doctor_name])).all()
            for u in users_to_remove:
                db.session.delete(u)

            patients_to_remove = Patient.query.filter(Patient.name.in_(['Patient A (Demo)', 'Patient B (Demo)', 'Patient C (Demo)'])).all()
            for p in patients_to_remove:
                # cascade delete is not configured; remove related vitals and alerts first
                PatientVital.query.filter_by(patient_id=p.id).delete()
                Alert.query.filter_by(patient_id=p.id).delete()
                db.session.delete(p)

            db.session.commit()

        # create users
        nurse = User.query.filter_by(name=demo_nurse_name).first()
        if not nurse:
            nurse = User(name=demo_nurse_name, role='nurse')
            db.session.add(nurse)

        doctor = User.query.filter_by(name=demo_doctor_name).first()
        if not doctor:
            doctor = User(name=demo_doctor_name, role='doctor')
            db.session.add(doctor)

        db.session.commit()

        # Create API tokens for demo users (if not set)
        import secrets
        if not nurse.api_token:
            nurse.api_token = secrets.token_urlsafe(24)
        if not doctor.api_token:
            doctor.api_token = secrets.token_urlsafe(24)
        db.session.commit()

        # create patients with demo demographic fields
        patients = []
        demo_specs = {
            'Patient A (Demo)': {'age': 72, 'sex': 'Female', 'room': '101A', 'weight_kg': 68, 'notes': 'Chronic hypertension (stable)'},
            'Patient B (Demo)': {'age': 58, 'sex': 'Male', 'room': '102B', 'weight_kg': 82, 'notes': 'COPD (baseline reduced SpO₂)'},
            'Patient C (Demo)': {'age': 45, 'sex': 'Female', 'room': '103C', 'weight_kg': 61, 'notes': 'No known chronic conditions'}
        }
        for pname in ['Patient A (Demo)', 'Patient B (Demo)', 'Patient C (Demo)']:
            p = Patient.query.filter_by(name=pname).first()
            if not p:
                spec = demo_specs.get(pname, {})
                p = Patient(name=pname, age=spec.get('age'), sex=spec.get('sex'), room=spec.get('room'), weight_kg=spec.get('weight_kg'), notes=spec.get('notes'))
                db.session.add(p)
                db.session.commit()
            else:
                # ensure demo fields exist for existing records
                spec = demo_specs.get(pname, {})
                updated = False
                for k, v in spec.items():
                    if getattr(p, k) != v:
                        setattr(p, k, v)
                        updated = True
                if updated:
                    db.session.commit()
            patients.append(p)

        # create initial vitals (some normal, some that will create alerts)
        # Patient A: high temp (critical)
        va, aa = create_vital_and_alerts(patients[0].id, heart_rate=78, temperature=38.5, spo2=97)
        print('Created for Patient A:', va, aa)

        # Patient B: low spo2 (critical)
        vb, ab = create_vital_and_alerts(patients[1].id, heart_rate=65, temperature=36.8, spo2=88)
        print('Created for Patient B:', vb, ab)

        # Patient C: mild warning HR
        vc, ac = create_vital_and_alerts(patients[2].id, heart_rate=110, temperature=37.0, spo2=96)
        print('Created for Patient C:', vc, ac)

        # Escalate one critical alert (Patient B) using DB update so doctor view shows it
        # Find one critical alert for Patient B
        critical_alert = Alert.query.filter_by(patient_id=patients[1].id, severity='critical').first()
        if critical_alert:
            critical_alert.escalated = True
            critical_alert.escalated_at = datetime.now(timezone.utc)
            critical_alert.escalated_by = nurse.id
            db.session.commit()
            print('Escalated alert id', critical_alert.id, 'for Patient B')

        print('\nSeeding complete:')
        print('  Nurse:', nurse.to_dict())
        print('  Doctor:', doctor.to_dict())
        print('  Patients:', [p.to_dict() for p in patients])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Remove prior demo data')
    args = parser.parse_args()
    seed(force=args.force)
