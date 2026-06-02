import os
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'chiave_segreta_assoluta_rate_that_site_12345'

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
            if 'reviews_data' not in session:
                session['reviews_data'] = []
            return redirect(url_for('index'))
    return '''
    
        Benvenuto su RateThatSite! ⭐️
        
            

            Entra nel sito
        
    
    '''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if request.method == 'POST':
        site_url = request.form.get('site_url', '').strip()
    else:
        site_url = request.args.get('url', '') or request.args.get('site_url', '')
        site_url = site_url.strip()

    if not site_url:
        return redirect(url_for('index'))

    tutte_le_recensioni = session.get('reviews_data', [])
    
    recensioni_trovate = []
    voti = []
    # Inizializziamo il conteggio per le barre delle valutazioni (da 1 a 5 stelle)
    conteggio_stelle = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for r in tutte_le_recensioni:
        if r.get('site_url') == site_url:
            recensioni_trovate.append(r)
            try:
                valore_voto = int(r['rating'])
                voti.append(valore_voto)
                if valore_voto in conteggio_stelle:
                    conteggio_stelle[valore_voto] += 1
            except:
                pass

    # Calcolo della media e delle percentuali per la barra di riepilogo grafico
    totale_recensioni = len(recensioni_trovate)
    media_voto = round(sum(voti) / totale_recensioni, 1) if totale_recensioni > 0 else 0

    percentuali_stelle = {}
    for stella, count in conteggio_stelle.items():
        percentuali_stelle[stella] = int((count / totale_recensioni) * 100) if totale_recensioni > 0 else 0

    return render_template(
        'risultati.html', 
        url_cercato=site_url, 
        recensioni=recensioni_trovate,
        media_voto=media_voto,
        totale_recensioni=totale_recensioni,
        percentuali=percentuali_stelle
    )

@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    autore = session.get('username', 'Anonimo')
    site_url = request.form.get('site_url', '').strip()
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating')
    
    # Recuperiamo l'immagine convertita in stringa base64 da JavaScript
    foto_base64 = request.form.get('foto_base64', '')

    nuova_recensione = {
        'autore': autore,
        'site_url': site_url,
        'comment': comment,
        'rating': int(rating),
        'foto_recensione': foto_base64 # Se vuota non mostrerà nulla, altrimenti caricherà la foto reale
    }
    
    recensioni_attuali = session.get('reviews_data', [])
    recensioni_attuali.append(nuova_recensione)
    session['reviews_data'] = recensioni_attuali
    session.modified = True
    
    return redirect(url_for('cerca', url=site_url))

@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    autore = session.get('username')
    tutte_le_recensioni = session.get('reviews_data', [])
    
    mie_recensioni = [r for r in tutte_le_recensioni if r.get('autore') == autore]
    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni, utente=autore)

if __name__ == '__main__':
    app.run(debug=True)
