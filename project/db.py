import sqlite3
from exchange import create_wallet_for_user

DB_FILE = "data/users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            pln REAL DEFAULT 500.0,
            btc REAL DEFAULT 0.0,
            usd REAL DEFAULT 150.0,
            btc_wallet TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_user(username):
    btc_address = create_wallet_for_user(username)
    if not btc_address:
        print("Failed to create wallet, user not inserted.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, btc_wallet) VALUES (?, ?)", (username, btc_address))
        conn.commit()
    except sqlite3.IntegrityError:
        print("User already exists.")
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
    c.execute("SELECT id, username, pln, btc, usd, btc_wallet FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "pln": row[2],
            "btc": row[3],
            "usd": row[4],
            "btc_wallet": row[5],
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