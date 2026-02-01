from app import create_app
app = create_app()
with app.app_context():
    client = app.test_client()
    from tools.seed_demo import seed
    seed(force=True)
    r = client.post('/patients/1/vitals', json={'temperature':38.7})
    print('post_vitals', r.status_code, r.get_json())
    alerts = r.get_json()['alerts_created']
    critical = next((a for a in alerts if a['severity']=='critical'), None)
    aid = critical['id']
    r = client.post(f'/alerts/{aid}/escalate', json={'escalated_by':1})
    print('escalate', r.status_code, r.get_json())
    r = client.get('/alerts/escalated', headers={'X-User-Id':'2'})
    print('doctor get escalated', r.status_code, r.get_json())
    r2 = client.get('/alerts/escalated')
    print('unauth get escalated', r2.status_code, r2.get_json())
