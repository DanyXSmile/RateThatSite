import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
# Usiamo una chiave fissa e sicura per evitare che la sessione scada a caso su Vercel
app.secret_key = 'chiave_segreta_assoluta_rate_that_site'

def get_db_connection():
    # Se siamo online su Vercel, forziamo il database in memoria
    if os.environ.get('VERCEL') or os.environ.get('NOW_REGION'):
        conn = sqlite3.connect(':memory:', check_same_thread=False)
    else:
        # In locale creiamo il file fisico pulito
        conn = sqlite3.connect('database.db', check_same_thread=False)
    
    # Assicuriamo che la tabella esista SEMPRE prima di restituire la connessione
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autore TEXT NOT NULL,
            site_url TEXT NOT NULL,
            comment TEXT NOT NULL,
            rating INTEGER,
            foto_recensione TEXT
        )
    ''')
    conn.commit()
    return conn

# 1. Controllo di sicurezza: se l'utente non ha un nome registrato nei cookie, lo mandiamo al login
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

# 2. Homepage principale
@app.route('/')
def index():
    return render_template('index.html')

# 3. Rotta per la Ricerca (Corretta per supportare sia POST che GET)
@app.route('/cerca', methods=['GET', 'POST'])
def cerca():
    if request.method == 'POST':
        site_url = request.form.get('site_url', '').strip()
    else:
        site_url = request.args.get('url', '').strip()

    if not site_url:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cerchiamo le recensioni per il sito selezionato
    cursor.execute('SELECT autore, comment, rating, foto_recensione FROM reviews WHERE site_url = ?', (site_url,))
    recensioni_trovate = cursor.fetchall()
    conn.close()
    
    return render_template('risultati.html', url_cercato=site_url, recensioni=recensioni_trovate)

# 4. Rotta per l'aggiunta di una recensione (con foto opzionale)
@app.route('/aggiungi_recensione', methods=['POST'])
def aggiungi_recensione():
    autore = session.get('username', 'Anonimo')
    site_url = request.form.get('site_url', '').strip()
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating')
    file_foto = request.files.get('foto')
    
    nome_file_salvato = None
    if file_foto and file_foto.filename != '':
        nome_file_salvato = f"{autore}_{file_foto.filename}"
        # Salviamo la foto solo se non siamo su Vercel (perché Vercel blocca la scrittura di file locali)
        if not os.environ.get('VERCEL') and not os.environ.get('NOW_REGION'):
            os.makedirs('static/uploads', exist_ok=True)
            file_foto.save(os.path.join('static/uploads', nome_file_salvato))
        else:
            # Segnaposto standard per evitare bug su Vercel
            nome_file_salvato = "placeholder.png"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO reviews (autore, site_url, comment, rating, foto_recensione) VALUES (?, ?, ?, ?, ?)',
                   (autore, site_url, comment, rating, nome_file_salvato))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 5. Profilo utente: Mostra tutte le recensioni dell'utente corrente
@app.route('/le-mie-recensioni')
def le_mie_recensioni():
    autore = session.get('username')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT site_url, comment, rating, foto_recensione FROM reviews WHERE autore = ?', (autore,))
    mie_recensioni = cursor.fetchall()
    conn.close()
    return render_template('le_mie_recensioni.html', recensioni=mie_recensioni, utente=autore)

if __name__ == '__main__':
    app.run(debug=True)