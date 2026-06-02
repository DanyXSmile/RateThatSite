import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Tabella recensioni semplificata
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
    conn.close()

if __name__ == '__main__':
    init_db()