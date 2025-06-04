import sqlite3
from exchange import create_wallet_for_user, get_rpc_connection, get_wallet_balance

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
    c.execute("""
        CREATE TABLE IF NOT EXISTS pending_tx (
            txid TEXT PRIMARY KEY,
            username TEXT,
            amount_btc REAL,
            pln REAL,
            usd REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_user(username, password):
    btc_address = create_wallet_for_user(username, password)
    if not btc_address:
        print("Failed to create wallet.")
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
    exists = bool(c.fetchone())
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

def save_pending_tx(txid, username, amount_btc, pln, usd, tx_type):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO pending_tx (txid, username, amount_btc, pln, usd, tx_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (txid, username, amount_btc, pln, usd, tx_type))
    conn.commit()
    conn.close()

def check_pending_transactions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT txid, username, amount_btc, pln, usd, tx_type FROM pending_tx")
    rows = c.fetchall()

    for txid, username, amount_btc, pln, usd, tx_type in rows:
        wallet = get_rpc_connection(wallet="Master")
        try:
            tx = wallet.gettransaction(txid)
            confirmations = tx.get("confirmations", 0)

            if confirmations >= 1:
                user_data = get_user(username)
                master_data = get_user("Master")

                if tx_type == "buy":
                    update_user_balances(username, user_data['pln'] - pln, user_data['usd'] - usd, float(get_wallet_balance(username)))
                    update_user_balances("Master", master_data['pln'] + pln, master_data['usd'] + usd, float(get_wallet_balance("Master")))

                elif tx_type == "sell":
                    update_user_balances(username, user_data['pln'] + pln, user_data['usd'] + usd, float(get_wallet_balance(username)))
                    update_user_balances("Master", master_data['pln'] - pln, master_data['usd'] - usd, float(get_wallet_balance("Master")))

                c.execute("DELETE FROM pending_tx WHERE txid = ?", (txid,))
                print(f"Transaction {txid} ({tx_type}) confirmed and processed.")

        except Exception as e:
            print(f"Error checking tx {txid}: {e}")

    conn.commit()
    conn.close()

def get_pending_transactions(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT txid, amount_btc, timestamp, tx_type FROM pending_tx WHERE username = ?", (username,))
    txs = c.fetchall()
    conn.close()
    return txs