import sqlite3

DB_FILE = "data/users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pln REAL DEFAULT 0.0,
            btc REAL DEFAULT 0.0,
            usd REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

def create_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def user_exists(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username, pln, btc, usd FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "pln": row[2],
            "btc": row[3],
            "usd": row[4],
        }
    return None

def update_user_balances(username, pln, usd, btc):
    conn = sqlite3.connect(DB_FILE) 
    c = conn.cursor()
    c.execute("""
        UPDATE users SET pln = ?, usd = ?, btc = ?
        WHERE username = ?
    """, (pln, usd, btc, username))
    conn.commit()
    conn.close()