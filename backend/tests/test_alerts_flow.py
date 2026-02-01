import json
import time


def post_vitals(client, patient_id, payload):
    return client.post(f'/patients/{patient_id}/vitals', json=payload)


def test_vitals_generate_alerts(client, demo_user_and_patient):
    patient = demo_user_and_patient['patient']

    # temp > 38 -> critical
    res = post_vitals(client, patient.id, {'heart_rate': 75, 'temperature': 38.5, 'spo2': 97})
    assert res.status_code == 201
    data = res.get_json()
    assert 'vital' in data
    alerts = data['alerts_created']
    assert any(a['severity'] == 'critical' and 'Temperature' in a['message'] for a in alerts)

    # spo2 < 90 -> critical
    res = post_vitals(client, patient.id, {'spo2': 88})
    assert res.status_code == 201
    alerts = res.get_json()['alerts_created']
    assert any(a['severity'] == 'critical' and 'SpO' in a['message'] for a in alerts)

    # hr outside 60-100 -> warning
    res = post_vitals(client, patient.id, {'heart_rate': 120})
    assert res.status_code == 201
    alerts = res.get_json()['alerts_created']
    assert any(a['severity'] == 'warning' and 'Heart Rate' in a['message'] for a in alerts)


def test_escalation_and_visibility(client, demo_user_and_patient, mocker):
    nurse = demo_user_and_patient['nurse']
    doctor = demo_user_and_patient['doctor']
    patient = demo_user_and_patient['patient']

    # create critical alert via vitals
    res = post_vitals(client, patient.id, {'temperature': 38.7})
    assert res.status_code == 201
    alerts = res.get_json()['alerts_created']
    critical = next((a for a in alerts if a['severity'] == 'critical'), None)
    assert critical is not None

    # mock the mailer to avoid network calls
    mocker.patch('app.utils.mailer.send_escalation_email', return_value=True)

    # escalate as nurse (valid)
    alert_id = critical['id']
    res = client.post(f'/alerts/{alert_id}/escalate', json={'escalated_by': nurse.id})
    assert res.status_code == 200
    data = res.get_json()
    assert data['alert']['escalated'] is True

    # doctor can fetch escalated alerts (authenticated)
    res = client.get('/alerts/escalated', headers={'X-User-Id': str(doctor.id)})
    assert res.status_code == 200
    es = res.get_json()
    assert any(a['id'] == alert_id for a in es)

    # non-doctor cannot fetch escalated alerts
    res = client.get('/alerts/escalated')
    assert res.status_code == 403


def test_invalid_escalation_rejections(client, demo_user_and_patient):
    nurse = demo_user_and_patient['nurse']
    patient = demo_user_and_patient['patient']

    # create a warning-level alert (heart rate)
    res = post_vitals(client, patient.id, {'heart_rate': 120})
    alerts = res.get_json()['alerts_created']
    warn_alert = next((a for a in alerts if a['severity'] == 'warning'), None)
    assert warn_alert is not None

    # trying to escalate non-critical alert should return 400
    res = client.post(f"/alerts/{warn_alert['id']}/escalate", json={'escalated_by': nurse.id})
    assert res.status_code == 400

    # trying to escalate without nurse identity should be rejected
    # first create a critical alert
    res = post_vitals(client, patient.id, {'temperature': 38.9})
    critical = next((a for a in res.get_json()['alerts_created'] if a['severity'] == 'critical'))
    assert critical

    res = client.post(f"/alerts/{critical['id']}/escalate", json={})
    assert res.status_code in (400, 403)
