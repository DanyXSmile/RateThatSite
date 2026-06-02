import os
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
# Chiave segreta per rendere sicuri e persistenti i dati salvati nei cookie dell'utente
app.secret_key = 'chiave_segreta_assoluta_rate_that_site_12345'

# Controllo iniziale: se l'utente non ha un nome profilo, lo forziamo a fare il login
@app.before_request
def richiedi_nome():
    if 'username' not in session and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('username', '').strip()
        if nome:
            session['username'] = nome
            # Inizializziamo una lista vuota di recensioni nei cookie se non esiste già
            if 'reviews_data' not in session:
                session['reviews_data'] = []
            return redirect(url_for('index'))
    return '''
    <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
        <h2>Benvenuto su RateThatSite! ⭐️</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Inserisci il tuo nome" required style="padding:10px; min-width:250px;"><br><br>
            <button type="submit" style="padding:10px 20px; background:#007bff; color:white; border:none; cursor:pointer;">Entra nel sito</button>
        </form>
    </div>
    '''

# 1. Homepage principale
@app.route('/')
def index():
    return render_template('index.html')

# 2. Rotta per la Ricerca (Cerca dentro la lista salvata nei cookie)
@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if request.method == 'POST':
        site_url = request.form.get('site_url', '').strip()
    else:
        site_url = request.args.get('url', '') or request.args.get('site_url', '')
        site_url = site_url.strip()

    if not site_url:
        return redirect(url_for('index'))

    # Recuperiamo tutte le recensioni salvate nei cookie (se non ci sono, usiamo una lista vuota)
    tutte_le_recensioni = session.get('reviews_data', [])
    
    # Filtriamo solo le recensioni che corrispondono all'URL cercato
    recensioni_trovate = []
    for r in tutte_le_recensioni:
        if r.get('site_url') == site_url:
            # Creiamo una tupla (autore, commento, voto, foto) per passarla al tuo vecchio template risultati.html senza romperlo
            recensioni_trovate.append((r['autore'], r['comment'], r['rating'], r.get('foto_recensione')))

    return render_template('risultati.html', url_cercato=site_url, recensioni=recensioni_trovate)

# 3. Rotta per l'aggiunta di una recensione (Salva dentro i cookie)
@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    autore = session.get('username', 'Anonimo')
    site_url = request.form.get('site_url', '').strip()
    # support legacy field name
    if not site_url:
        site_url = request.form.get('url_sito', '').strip()
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating')
    
    # Creiamo il dizionario della nuova recensione
    nuova_recensione = {
        'autore': autore,
        'site_url': site_url,
        'comment': comment,
        'rating': rating,
        'foto_recensione': 'placeholder.png'
    }
    
    # Estraiamo la lista attuale, aggiungiamo la recensione e risalviamo nella sessione
    recensioni_attuali = session.get('reviews_data', [])
    recensioni_attuali.append(nuova_recensione)
    session['reviews_data'] = recensioni_attuali
    
    # Diciamo a Flask che la sessione è stata modificata e deve aggiornare il cookie del browser
    session.modified = True
    
    return redirect(url_for('index'))

# 4. Profilo utente: Mostra tutte le recensioni scritte dall'utente corrente
@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    autore = session.get('username')
    tutte_le_recensioni = session.get('reviews_data', [])
    
    # Filtriamo le recensioni dove l'autore corrisponde all'utente loggato
    mie_recensioni = []
    for r in tutte_le_recensioni:
        if r.get('autore') == autore:
            mie_recensioni.append((r['site_url'], r['comment'], r['rating'], r.get('foto_recensione')))
            
    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni, utente=autore)

if __name__ == '__main__':
    app.run(debug=True)
