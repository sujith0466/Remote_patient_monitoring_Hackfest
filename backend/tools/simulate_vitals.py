"""
CLI tool to generate simulated vitals for patients.

Usage examples:
  python simulate_vitals.py --interval 10 --count 50
  python simulate_vitals.py --once
  python simulate_vitals.py --patient-ids 1 2 3 --interval 5
"""
import time
import argparse
import random
from app import create_app, db
from app.models import Patient
from app.utils.simulator import generate_random_vitals, create_vital_and_alerts


def main():
    parser = argparse.ArgumentParser(description='Simulate patient vitals for demo')
    parser.add_argument('--interval', type=float, default=10.0, help='Seconds between generation cycles')
    parser.add_argument('--count', type=int, default=0, help='Number of cycles to run (0 = infinite)')
    parser.add_argument('--patient-ids', type=int, nargs='*', help='Specific patient ids to simulate (default: all)')
    parser.add_argument('--once', action='store_true', help='Run one round and exit')
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        if args.patient_ids:
            patients = Patient.query.filter(Patient.id.in_(args.patient_ids)).all()
        else:
            patients = Patient.query.all()

        if not patients:
            print('No patients found in DB. Add patients or run seed script.')
            return

        def run_cycle():
            print('Running generation cycle for patients:', [p.id for p in patients])
            for p in patients:
                # generate random vitals
                v = generate_random_vitals()
                vital, alerts = create_vital_and_alerts(p.id, **v)
                print(f'Patient {p.id}: vital={vital}')
                for a in alerts:
                    print(f'  Created alert: {a}')

        if args.once or args.count == 1:
            run_cycle()
            return

        cycles = args.count
        i = 0
        try:
            while cycles == 0 or i < cycles:
                run_cycle()
                i += 1
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print('\nSimulation stopped by user')

if __name__ == '__main__':
    main()
