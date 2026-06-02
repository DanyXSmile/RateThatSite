from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chiave_semplice_segreta'

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

@app.route('/')
def index():
    return render_template('index.html')

# 2. MOTORE DI RICERCA
@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if request.method == 'POST':
        url_cercato = request.form.get('url_sito') or request.form.get('url')
    else:
        url_cercato = request.args.get('url')

    if not url_cercato:
        return redirect('/')
    
    connessione = sqlite3.connect('database.db')
    connessione.row_factory = sqlite3.Row
    cursore = connessione.cursor()
    
    # Cerchiamo se ci sono recensioni per questo URL
    cursore.execute("SELECT * FROM reviews WHERE site_url = ?", (url_cercato,))
    recensioni_trovate = cursore.fetchall()
    connessione.close()
    
    if len(recensioni_trovate) > 0:
        total_reviews = len(recensioni_trovate)
        star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        total_stars = 0

        for r in recensioni_trovate:
            rating = int(r['rating']) if r['rating'] is not None else 0
            if rating in star_counts:
                star_counts[rating] += 1
                total_stars += rating

        avg_rating = round(total_stars / total_reviews, 1) if total_reviews > 0 else 0
        star_percentages = {
            5: (star_counts[5] / total_reviews * 100) if total_reviews > 0 else 0,
            4: (star_counts[4] / total_reviews * 100) if total_reviews > 0 else 0,
            3: (star_counts[3] / total_reviews * 100) if total_reviews > 0 else 0,
            2: (star_counts[2] / total_reviews * 100) if total_reviews > 0 else 0,
            1: (star_counts[1] / total_reviews * 100) if total_reviews > 0 else 0,
        }

        return render_template(
            'risultati.html', 
            url=url_cercato, 
            recensioni=recensioni_trovate,
            avg_rating=avg_rating,
            star_counts=star_counts,
            star_percentages=star_percentages,
            total_reviews=total_reviews
        )
    else:
        return render_template('nuova_recensione.html', url=url_cercato)

@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    autore = session.get('username')
    site_url = request.form.get('url_sito')
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    file_foto = request.files.get('foto')

    nome_file_salvato = None
    if file_foto and file_foto.filename != '':
        os.makedirs('static/uploads', exist_ok=True)
        nome_file_salvato = f"{autore}_{file_foto.filename}"
        file_foto.save(os.path.join('static/uploads', nome_file_salvato))

    connessione = sqlite3.connect('database.db')
    cursore = connessione.cursor()
    cursore.execute(
        'INSERT INTO reviews (autore, site_url, comment, rating, foto_recensione) VALUES (?, ?, ?, ?, ?)',
        (autore, site_url, comment, rating, nome_file_salvato)
    )
    connessione.commit()
    connessione.close()

    return redirect(url_for('index'))

@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    autore = session.get('username')
    connessione = sqlite3.connect('database.db')
    connessione.row_factory = sqlite3.Row
    cursore = connessione.cursor()
    cursore.execute('SELECT site_url, comment, rating, foto_recensione FROM reviews WHERE autore = ?', (autore,))
    mie_recensioni = cursore.fetchall()
    connessione.close()

    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni, utente=autore)

if __name__ == '__main__':
    app.run(debug=True)