Render deployment steps — CareWatch backend

1) Add a Render Web Service
   - Name: carewatch-backend
   - Environment: Python
   - Branch: your desired branch

2) Add Managed Postgres (or external DB)
   - Create a Render Managed Database or use an existing Postgres.
   - Copy the database URL into the Web Service environment variable: `DATABASE_URL`.

3) Environment variables (set in Render Service settings)
   - `DATABASE_URL` = (postgres connection string)
   - `CORS_ORIGINS` = (your frontend URL, e.g. `https://your-frontend.onrender.com`)
   - Optional SMTP vars: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`, `ALERT_EMAIL_RECIPIENTS`

4) Build & Start
   - Build command: `pip install -r requirements.txt`
   - Start command: `bash -lc "python -c 'from app import create_app, db; app=create_app(); ctx=app.app_context(); ctx.push(); db.create_all(); ctx.pop()' && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2"`

5) Seed demo data (once deployed)
   - Use the Render dashboard "Shell" to run:
     `python tools/seed_demo.py --force`
   - Confirm: `https://<your-backend>/patients` returns seeded demo patients

Deployment checklist (quick)
- ✅ Set `DATABASE_URL` to your Postgres connection string
- ✅ Set `CORS_ORIGINS` to your frontend URL (e.g. `https://your-frontend.onrender.com`)
- ✅ Set `VITE_API_BASE` in the frontend service to your backend URL (e.g. `https://your-backend.onrender.com`)
- ✅ Seed demo users/patients with `python tools/seed_demo.py --force` so demo tokens are available for judges to test
- ✅ Optional: Set SMTP env vars if you want email notifications in production

Optional: Use the included `render.yaml` to create both the backend and frontend services in Render automatically. You can import this manifest when creating or configuring services in the Render dashboard (it predefines build/start commands and placeholders for env vars).

Notes & recommendations
- Use Postgres (not SQLite) for persistent storage on Render.
- For production, replace `run_dev` with a proper WSGI factory if required; run migrations with Alembic/Flask-Migrate.
- If you want, I can also add a short `backend/.render.yaml` for consistent render settings and/or add a CI workflow that runs tests on PRs.
