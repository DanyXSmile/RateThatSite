import os
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ratethatsite_ultra_secure_key_2026")

# DATABASE IN MEMORIA (Previene il crash dei cookie a 4KB e supporta le foto)
# Contiene alcune recensioni iniziali per far funzionare la linea animata scorrevole
MOCK_DB = {
    "utenti": ["Daniil", "Aura", "Marco", "Sofia"],
    "recensioni": [
        {"autore": "Aura", "site_url": "github.com", "comment": "GitHub mi ha salvato la vita, essenziale per programmare!", "rating": 5, "foto_recensione": ""},
        {"autore": "Marco", "site_url": "google.com", "comment": "Il motore di ricerca migliore di sempre, pulito e veloce.", "rating": 5, "foto_recensione": ""},
        {"autore": "Sofia", "site_url": "spotify.com", "comment": "Ottima app per la musica, ma la pubblicità nella versione free è troppa.", "rating": 3, "foto_recensione": ""},
        {"autore": "Daniil", "site_url": "vercel.com", "comment": " some bug all'inizio ma il deploy dei siti web è istantaneo. Fantastico.", "rating": 4, "foto_recensione": ""}
    ]
}

@app.before_request
def richiedi_nome():
    if 'username' not in session and request.endpoint not in ['login', 'static']:
        return redirect(url_for('index'))

@app.route('/')
def index():
    if 'username' not in session:
        return render_template('index.html', mostre_login=True, errore_user=None)
    return render_template('index.html', mostre_login=False, recensioni_loop=MOCK_DB['recensioni'])

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    if not username:
        return redirect(url_for('index'))

    if username in MOCK_DB['utenti'] or username.lower() in [u.lower() for u in MOCK_DB['utenti']]:
        return render_template('index.html', mostre_login=True, errore_user="Questo username è già in uso. Scegline un altro!")

    MOCK_DB['utenti'].append(username)
    session['username'] = username
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        url_cercato = request.form.get('site_url', '').strip().lower()
        url_cercato = url_cercato.replace('https://', '').replace('http://', '').replace('www.', '')
        if url_cercato.endswith('/'):
            url_cercato = url_cercato[:-1]
    else:
        url_cercato = request.args.get('url', '').strip().lower()

    if not url_cercato:
        return redirect(url_for('index'))

    recensioni_sito = [r for r in MOCK_DB['recensioni'] if r['site_url'] == url_cercato]

    totale_recensioni = len(recensioni_sito)
    media_stelle = 0
    conteggio_stelle = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    percentuali = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    if totale_recensioni > 0:
        somma = 0
        for r in recensioni_sito:
            somma += r['rating']
            conteggio_stelle[r['rating']] += 1
        media_stelle = round(somma / totale_recensioni, 1)
        for stella in conteggio_stelle:
            percentuali[stella] = round((conteggio_stelle[stella] / totale_recensioni) * 100)

    return render_template(
        'risultati.html',
        url_cercato=url_cercato,
        recensioni=recensioni_sito,
        totale_recensioni=totale_recensioni,
        media_stelle=media_stelle,
        conteggio_stelle=conteggio_stelle,
        percentuali=percentuali
    )

@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    if 'username' not in session:
        return redirect(url_for('index'))

    autore = session['username']
    site_url = request.form.get('site_url', '').strip().lower()
    comment = request.form.get('comment', '').strip()
    rating = int(request.form.get('rating', 5))
    foto_base64 = request.form.get('foto_base64', '')

    nuova_recensione = {
        'autore': autore,
        'site_url': site_url,
        'comment': comment,
        'rating': rating,
        'foto_recensione': foto_base64
    }

    MOCK_DB['recensioni'].append(nuova_recensione)
    return redirect(url_for('cerca', url=site_url))

@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    if 'username' not in session:
        return redirect(url_for('index'))

    mie_recensioni = [r for r in MOCK_DB['recensioni'] if r['autore'] == session['username']]
    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
