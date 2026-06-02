from app import app

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['username'] = 'tester'
    resp = client.post('/cerca', data={'site_url': 'https://example.com'})
    print('STATUS:', resp.status_code)
    print(resp.get_data(as_text=True))
