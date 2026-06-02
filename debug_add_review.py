from app import app

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['username'] = 'tester'
    # submit a review using the actual form field name 'url_sito'
    resp = client.post('/aggiungi_recensione', data={
        'url_sito': 'https://example.com',
        'comment': 'Great site',
        'rating': '5'
    }, follow_redirects=True)
    print('POST STATUS:', resp.status_code)
    # fetch my reviews
    resp2 = client.get('/le-mie-recensioni')
    print('PROFILE STATUS:', resp2.status_code)
    print(resp2.get_data(as_text=True))
