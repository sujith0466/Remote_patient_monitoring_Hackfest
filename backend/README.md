# CareWatch Backend (Flask)

Minimal Flask backend skeleton for CareWatch hackathon project.

Features included:
- SQLAlchemy models: User, Patient, Vital, Alert
- REST endpoints (no auth yet):
  - GET /users
  - GET /patients
  - POST /patients/<id>/vitals  (creates vitals and rule-based alerts)
  - GET /alerts (?escalated=true)
  - POST /alerts/<id>/escalate  (nurse escalates critical alert)

Setup (local development):

1. Create a virtualenv and install requirements:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Configure database (MySQL) in `.env` based on `.env.example` or set `DATABASE_URL` env var.

3. Initialize database and run migrations (uses Flask-Migrate):

   flask db init
   flask db migrate -m "initial"
   flask db upgrade

4. Run the app:

   python run.py

Simulating vitals (demo):

- CLI: generate vitals once for all patients

   python tools\simulate_vitals.py --once

- CLI: run continuous generation every 10 seconds

   python tools\simulate_vitals.py --interval 10

- CLI: run N cycles (e.g., 20 cycles)

   python tools\simulate_vitals.py --interval 5 --count 20

- CLI: simulate only specific patients

   python tools\simulate_vitals.py --patient-ids 1 2 3 --once

- CLI: seed demo data (users, patients, initial vitals & alerts)

   python tools\seed_demo.py

- CLI: re-seed (remove prior demo entries created by the script)

   python tools\seed_demo.py --force

Note: run the above from the `backend` folder using the virtualenv Python (e.g., `.venv\Scripts\python tools\simulate_vitals.py` or `.venv\Scripts\python tools\seed_demo.py`).
Notes:
- This skeleton implements rule-based alerts only (no diagnosis), and only basic persistence and escalation handling.
- Email/alert delivery will be integrated later (SendGrid / SMTP) as specified in project plan.
