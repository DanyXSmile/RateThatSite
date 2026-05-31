from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 1. HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# 2. MOTORE DI RICERCA
@app.route('/cerca', methods=['POST'])
def cerca():
    url_cercato = request.form.get('url_sito')
    
    connessione = sqlite3.connect('database.db')
    cursore = connessione.cursor()
    
    # Cerchiamo se ci sono recensioni per questo URL
    cursore.execute("SELECT * FROM recensioni WHERE url_sito = ?", (url_cercato,))
    recensioni_trovate = cursore.fetchall()
    connessione.close()
    
    if len(recensioni_trovate) > 0:
        # Se ci sono recensioni, carichiamo la pagina dei risultati passandogli i dati
        return render_template('risultati.html', url=url_cercato, recensioni=recensioni_trovate)
    else:
        # Se non ci sono, mostriamo il form per aggiungerne una
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