import os
import sys
import signal
import shutil
import subprocess
from pathlib import Path
from app import create_app, db

# Local dev launcher: starts frontend (npm run dev) and backend together when run as script.
app = create_app()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'


# ----------------------------
# SAFE: health/status endpoint
# ----------------------------
@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "CareWatch backend is running",
        "frontend": "Open the Vite dev server URL shown in terminal (usually http://localhost:5173)"
    }


def _start_frontend():
    """Spawn the frontend dev server (npm run dev). Returns Popen or None if npm not found."""
    npm_exec = shutil.which('npm') or shutil.which('npm.cmd')
    if not npm_exec:
        print(
            'npm not found in PATH — frontend dev server will NOT be started.\n'
            'Start it manually with `npm run dev` inside the frontend folder.'
        )
        return None

    env = os.environ.copy()
    env.setdefault('VITE_API_BASE', env.get('VITE_API_BASE', 'http://localhost:5000'))

    try:
        print(f'Starting frontend dev server in {FRONTEND_DIR}...')
        proc = subprocess.Popen(
            [npm_exec, 'run', 'dev'],
            cwd=str(FRONTEND_DIR),
            env=env
        )
        return proc
    except Exception as e:
        print('Failed to start frontend dev server:', e)
        return None


if __name__ == "__main__":
    # Ensure DB tables exist and seed demo data if DB is empty
    with app.app_context():
        db.create_all()
        try:
            from app.models import Patient
            if not Patient.query.first():
                try:
                    print('Seeding demo data (database empty)...')
                    from tools.seed_demo import seed
                    seed(force=True)
                except Exception as e:
                    print('Seeding failed:', e)
        except Exception:
            pass

    frontend_proc = _start_frontend()
    _cleanup_state = {"done": False}  # ✅ mutable, no scoping issues

    def _cleanup(signum=None, frame=None):
        if _cleanup_state["done"]:
            return
        _cleanup_state["done"] = True

        print('\nShutting down...')
        try:
            if frontend_proc and frontend_proc.poll() is None:
                print('Terminating frontend process...')
                frontend_proc.terminate()
                frontend_proc.wait(timeout=5)
        except Exception:
            pass
        finally:
            os._exit(0)

    # Handle Ctrl+C and terminal close (Windows-safe)
    signal.signal(signal.SIGINT, _cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _cleanup)

    app.run(debug=True, use_reloader=False)
