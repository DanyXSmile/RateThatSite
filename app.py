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
        site_url = request.form.get('site_url', '').strip()
    else:
        site_url = request.args.get('url', '').strip()

    if not site_url:
        return redirect(url_for('index'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT autore, comment, rating, foto_recensione FROM reviews WHERE site_url = ?', (site_url,))
    recensioni_trovate = cursor.fetchall()
    conn.close()

    return render_template('risultati.html', url_cercato=site_url, recensioni=recensioni_trovate)

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