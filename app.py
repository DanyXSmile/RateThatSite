import os
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ratethatsite_safe_key_2026")

# DATABASE SALVATO SUL SERVER (Evita crash di memoria e supporta le foto)
DB = {
    "utenti": ["Daniil", "Aura", "Marco", "Sofia"],
    "recensioni": [
        {"autore": "Aura", "site_url": "github.com", "comment": "GitHub è fondamentale per salvare il codice, super consigliato!", "rating": 5, "foto": ""},
        {"autore": "Marco", "site_url": "google.com", "comment": "Sempre pulito e velocissimo, il re dei motori di ricerca.", "rating": 5, "foto": ""},
        {"autore": "Sofia", "site_url": "spotify.com", "comment": "La selezione musicale è ottima, ma gli annunci free sono un po' troppi.", "rating": 3, "foto": ""},
        {"autore": "Daniil", "site_url": "vercel.com", "comment": "Interfaccia pulita per i deploy, integrazione fantastica.", "rating": 4, "foto": ""}
    ]
}

@app.route('/')
def index():
    # Se l'utente non è loggato, mostriamo subito la schermata che chiede il nome
    if 'username' not in session:
        return render_template('index.html', mostra_login=True, errore_user=None, recensioni_loop=DB["recensioni"])
    return render_template('index.html', mostra_login=False, errore_user=None, recensioni_loop=DB["recensioni"])

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    if not username:
        return redirect(url_for('index'))
    
    # Controllo Username Unico (Case-Insensitive)
    if username.lower() in [u.lower() for u in DB["utenti"]]:
        return render_template('index.html', mostra_login=True, errore_user="Questo utente è già in uso", recensioni_loop=DB["recensioni"])
    
    # Registrazione utente riuscita
    DB["utenti"].append(username)
    session['username'] = username
    return redirect(url_for('index'))

@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if 'username' not in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        url_cercato = request.form.get('site_url', '').strip().lower()
        # Pulizia dell'URL per raggruppare i risultati in modo uniforme
        url_cercato = url_cercato.replace("https://", "").replace("http://", "").replace("www.", "")
        if url_cercato.endswith('/'):
            url_cercato = url_cercato[:-1]
    else:
        url_cercato = request.args.get('url', '').strip()

    if not url_cercato:
        return redirect(url_for('index'))

    # Filtra le recensioni abbinate a questo URL
    recensioni_sito = [r for r in DB["recensioni"] if r['site_url'] == url_cercato]
    totale = len(recensioni_sito)
    
    media_stelle = 0
    conteggio_stelle = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    percentuali = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    if totale > 0:
        somma = sum(r['rating'] for r in recensioni_sito)
        media_stelle = round(somma / totale, 1)
        for r in recensioni_sito:
            conteggio_stelle[r['rating']] += 1
        for stella in conteggio_stelle:
            percentuali[stella] = round((conteggio_stelle[stella] / totale) * 100)

    return render_template(
        'risultati.html',
        url_cercato=url_cercato,
        recensioni=recensioni_sito,
        totale_recensioni=totale,
        media_stelle=media_stelle,
        conteggio_stelle=conteggio_stelle,
        percentuali=percentuali
    )

@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    if 'username' not in session:
        return redirect(url_for('index'))

    site_url = request.form.get('site_url', '').strip().lower()
    comment = request.form.get('comment', '').strip()
    rating = int(request.form.get('rating', 5))
    foto_base64 = request.form.get('foto_base64', '')

    nuova_recensione = {
        'autore': session['username'],
        'site_url': site_url,
        'comment': comment,
        'rating': rating,
        'foto': foto_base64
    }
    DB["recensioni"].append(nuova_recensione)
    return redirect(url_for('cerca', url=site_url))

@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    if 'username' not in session:
        return redirect(url_for('index'))
    mie_recensioni = [r for r in DB["recensioni"] if r['autore'] == session['username']]
    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni)

@app.route('/chi-siamo')
def chi_siamo():
    return render_template('chi_siamo.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/elimina_recensione', methods=['POST'])
def elimina_recensione():
    if 'username' not in session:
        return redirect(url_for('index'))

    site_url = request.form.get('site_url', '').strip()
    comment = request.form.get('comment', '').strip()

    DB["recensioni"] = [
        r for r in DB["recensioni"]
        if not (r['autore'] == session['username'] and r['site_url'] == site_url and r['comment'] == comment)
    ]
    
    return redirect(url_for('le_mie_recensioni'))

if __name__ == '__main__':
    app.run(debug=True)
