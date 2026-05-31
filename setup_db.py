import sqlite3

# Crea (o si collega a) un file chiamato database.db
connessione = sqlite3.connect('database.db')

# Il cursore serve per eseguire i comandi SQL
cursore = connessione.cursor()

# Scriviamo il comando SQL per creare la tabella
cursore.execute('''
    CREATE TABLE IF NOT EXISTS recensioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_sito TEXT NOT NULL,
        autore TEXT NOT NULL,
        testo_recensione TEXT NOT NULL,
        voto INTEGER NOT NULL
    )
''')

# Salviamo le modifiche e chiudiamo la connessione
connessione.commit()
connessione.close()

print("Database e tabella creati con successo!")