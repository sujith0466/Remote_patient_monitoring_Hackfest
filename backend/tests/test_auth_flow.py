import pytest


def test_escalation_requires_nurse_auth(client, demo_user_and_patient):
    nurse = demo_user_and_patient['nurse']
    doctor = demo_user_and_patient['doctor']
    patient = demo_user_and_patient['patient']

    # create a critical alert
    res = client.post(f'/patients/{patient.id}/vitals', json={'temperature': 38.8})
    assert res.status_code == 201
    alerts = res.get_json()['alerts_created']
    critical = next((a for a in alerts if a['severity'] == 'critical'), None)
    assert critical
    aid = critical['id']

    # escalate without auth -> should be rejected (missing escalated_by)
    r = client.post(f'/alerts/{aid}/escalate', json={})
    assert r.status_code in (400, 401, 403)

    # escalate with doctor token -> forbidden
    r = client.post(f'/alerts/{aid}/escalate', json={}, headers={'Authorization': f'Token {doctor.api_token}'})
    assert r.status_code in (400, 401, 403)

    # escalate with nurse token -> allowed
    r = client.post(f'/alerts/{aid}/escalate', json={}, headers={'Authorization': f'Token {nurse.api_token}'})
    assert r.status_code == 200


def test_escalated_list_requires_doctor_auth(client, demo_user_and_patient):
    nurse = demo_user_and_patient['nurse']
    doctor = demo_user_and_patient['doctor']
    patient = demo_user_and_patient['patient']

    # create and escalate an alert as nurse
    res = client.post(f'/patients/{patient.id}/vitals', json={'temperature': 38.9})
    critical = next((a for a in res.get_json()['alerts_created'] if a['severity'] == 'critical'))
    aid = critical['id']
    r = client.post(f'/alerts/{aid}/escalate', json={}, headers={'Authorization': f'Token {nurse.api_token}'})
    assert r.status_code == 200

    # fetch escalated without auth -> forbidden
    r = client.get('/alerts/escalated')
    assert r.status_code == 403

    # fetch with nurse token -> forbidden
    r = client.get('/alerts/escalated', headers={'Authorization': f'Token {nurse.api_token}'})
    assert r.status_code == 403

    # fetch with doctor token -> allowed
    r = client.get('/alerts/escalated', headers={'Authorization': f'Token {doctor.api_token}'})
    assert r.status_code == 200
