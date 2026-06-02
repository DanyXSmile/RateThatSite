from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 1. HOME PAGE
@app.route('/')
def home():
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
    cursore.execute("SELECT * FROM recensioni WHERE url_sito = ?", (url_cercato,))
    recensioni_trovate = cursore.fetchall()
    connessione.close()
    
    if len(recensioni_trovate) > 0:
        total_reviews = len(recensioni_trovate)
        star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        total_stars = 0

        for r in recensioni_trovate:
            voto = int(r['voto'])
            if voto in star_counts:
                star_counts[voto] += 1
                total_stars += voto

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

# 3. SALVATAGGIO DATI DAL FORM
@app.route('/salva_recensione', methods=['POST'])
def salva_recensione():
    # Recuperiamo i dati inviati dal form di nuova_recensione.html
    url = request.form.get('url_sito')
    autore = request.form.get('autore')
    testo = request.form.get('testo_recensione')
    voto = request.form.get('voto')
    
    # Ci colleghiamo al database per inserire il nuovo record
    connessione = sqlite3.connect('database.db')
    cursore = connessione.cursor()
    
    # Comando SQL per inserire i dati nei 5 campi significativi
    cursore.execute('''
        INSERT INTO recensioni (url_sito, autore, testo_recensione, voto)
        VALUES (?, ?, ?, ?)
    ''', (url, autore, testo, voto))
    
    connessione.commit() # Salva definitivamente i dati nel file .db
    connessione.close()
    
    # Messaggio di successo temporaneo che rimanda alla home
    return f"<h1>Recensione salvata con successo per {url}!</h1><p><a href='/'>Torna alla Home per cercarlo di nuovo</a></p>"

if __name__ == '__main__':
    app.run(debug=True)