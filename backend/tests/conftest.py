import os
import sys
import pytest
import unittest.mock

# Ensure project root (backend) is on sys.path so `import app` resolves during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app, db
from app.models import User, Patient


@pytest.fixture
def app_instance(tmp_path, monkeypatch):
    # set DATABASE_URL before app creation so SQLAlchemy uses sqlite in-memory
    import os
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SMTP_SERVER': None,
        'ALERT_EMAIL_RECIPIENTS': []
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


@pytest.fixture
def runner(app_instance):
    return app_instance.test_cli_runner()


@pytest.fixture
def demo_user_and_patient(app_instance):
    from app import db
    import secrets
    nurse = User(name='Test Nurse', role='nurse')
    doctor = User(name='Test Doctor', role='doctor')
    db.session.add_all([nurse, doctor])
    db.session.commit()

    # assign API tokens for tests
    nurse.api_token = secrets.token_urlsafe(24)
    doctor.api_token = secrets.token_urlsafe(24)
    db.session.commit()

    p = Patient(name='Test Patient')
    db.session.add(p)
    db.session.commit()

    return { 'nurse': nurse, 'doctor': doctor, 'patient': p }


# Fallback for environments where pytest-mock isn't installed/enabled.
# If pytest-mock is present, it will provide its own `mocker` fixture and this
# fixture will simply be ignored (fixture name collision is resolved by plugin
# precedence). In practice, this keeps tests runnable with minimal deps.
@pytest.fixture
def mocker(request):
    class _Mocker:
        def patch(self, target, *args, **kwargs):
            p = unittest.mock.patch(target, *args, **kwargs)
            obj = p.start()
            request.addfinalizer(p.stop)
            return obj

    return _Mocker()
