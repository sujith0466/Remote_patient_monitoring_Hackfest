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
            users_to_remove = User.query.filter(User.email.in_(['nurse@example.com', 'doctor@example.com'])).all()
            for u in users_to_remove:
                db.session.delete(u)

            patients_to_remove = Patient.query.filter(Patient.name.in_(['Ramesh Kumar', 'Anita Sharma', 'Rahul Verma'])).all()
            for p in patients_to_remove:
                # cascade delete is not configured; remove related vitals and alerts first
                PatientVital.query.filter_by(patient_id=p.id).delete()
                Alert.query.filter_by(patient_id=p.id).delete()
                db.session.delete(p)

            db.session.commit()

        # create users
        nurse = User.query.filter_by(email='nurse@example.com').first()
        if not nurse:
            nurse = User(name='Demo Nurse', email='nurse@example.com', role='nurse')
            nurse.set_password('password') # Set a default password for demo
            db.session.add(nurse)

        doctor = User.query.filter_by(email='doctor@example.com').first()
        if not doctor:
            doctor = User(name='Demo Doctor', email='doctor@example.com', role='doctor')
            doctor.set_password('password') # Set a default password for demo
            db.session.add(doctor)

        # Add new nurse@gmail.com
        nurse_gmail = User.query.filter_by(email='nurse@gmail.com').first()
        if not nurse_gmail:
            nurse_gmail = User(name='Demo Nurse Gmail', email='nurse@gmail.com', role='nurse')
            nurse_gmail.set_password('nurse1234')
            db.session.add(nurse_gmail)

        # Add new doctor@gmail.com
        doctor_gmail = User.query.filter_by(email='doctor@gmail.com').first()
        if not doctor_gmail:
            doctor_gmail = User(name='Demo Doctor Gmail', email='doctor@gmail.com', role='doctor')
            doctor_gmail.set_password('doctor1234')
            db.session.add(doctor_gmail)

        db.session.commit()

        # Create API tokens for demo users (if not set)
        import secrets
        if not nurse.api_token:
            nurse.api_token = secrets.token_urlsafe(24)
        if not doctor.api_token:
            doctor.api_token = secrets.token_urlsafe(24)
        db.session.commit()

        # create patients with demo demographic fields and specific conditions
        patients = []
        demo_specs = {
            'Ramesh Kumar': {'age': 72, 'sex': 'Male', 'room': '201A', 'weight_kg': 75, 'notes': 'History of cardiac issues.'},
            'Anita Sharma': {'age': 58, 'sex': 'Female', 'room': '202B', 'weight_kg': 62, 'notes': 'Recent respiratory infection.'},
            'Rahul Verma': {'age': 45, 'sex': 'Male', 'room': '203C', 'weight_kg': 80, 'notes': 'Post-operative recovery.'}
        }
        patient_names = ['Ramesh Kumar', 'Anita Sharma', 'Rahul Verma']

        for pname in patient_names:
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

        # create initial vitals to trigger specific alerts
        # Ramesh Kumar (critical): high temp and low spo2
        print('Creating vitals for Ramesh Kumar (critical)...')
        va, aa = create_vital_and_alerts(patients[0].id, heart_rate=90, temperature=38.6, spo2=88)
        print('Created for Ramesh Kumar:', va, aa)

        # Anita Sharma (warning): high heart rate
        print('Creating vitals for Anita Sharma (warning)...')
        vb, ab = create_vital_and_alerts(patients[1].id, heart_rate=115, temperature=37.1, spo2=95)
        print('Created for Anita Sharma:', vb, ab)

        # Rahul Verma (stable): normal vitals
        print('Creating vitals for Rahul Verma (stable)...')
        vc, ac = create_vital_and_alerts(patients[2].id, heart_rate=70, temperature=36.9, spo2=98)
        print('Created for Rahul Verma:', vc, ac)

        # Escalate one critical alert (Ramesh Kumar) using DB update so doctor view shows it
        # Find one critical alert for Ramesh Kumar
        critical_alert = Alert.query.filter_by(patient_id=patients[0].id, severity='critical').first()
        if critical_alert:
            critical_alert.escalated = True
            critical_alert.escalated_at = datetime.now(timezone.utc)
            critical_alert.escalated_by = nurse.id # Nurse escalates
            db.session.commit()
            print('Escalated alert id', critical_alert.id, 'for Ramesh Kumar')

        print('\nSeeding complete:')
        print('  Nurse:', nurse.to_dict())
        print('  Doctor:', doctor.to_dict())
        print('  Patients:', [p.to_dict() for p in patients])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Remove prior demo data')
    args = parser.parse_args()
    seed(force=args.force)
