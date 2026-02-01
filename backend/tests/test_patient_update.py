import pytest


def test_patient_update_requires_auth(client, demo_user_and_patient):
    patient = demo_user_and_patient['patient']

    res = client.patch(f'/patients/{patient.id}', json={'age': 51})
    assert res.status_code == 401


def test_nurse_can_update_patient(client, demo_user_and_patient):
    nurse = demo_user_and_patient['nurse']
    patient = demo_user_and_patient['patient']

    res = client.patch(f'/patients/{patient.id}', json={'room': '2B'}, headers={'Authorization': f'Token {nurse.api_token}'})
    assert res.status_code == 200
    j = res.get_json()
    assert j['room'] == '2B'


def test_doctor_can_update_patient(client, demo_user_and_patient):
    doctor = demo_user_and_patient['doctor']
    patient = demo_user_and_patient['patient']

    res = client.patch(f'/patients/{patient.id}', json={'notes': 'Seen by Dr.'}, headers={'Authorization': f'Token {doctor.api_token}'})
    assert res.status_code == 200
    j = res.get_json()
    assert j['notes'] == 'Seen by Dr.'
