# db.py
import sqlite3

conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    wallet TEXT DEFAULT '',
    active_investment INTEGER DEFAULT 0,
    pending_profit REAL DEFAULT 0
)""")
conn.commit()

# --- دوال مساعدة ---
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def update_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def set_wallet(user_id, wallet):
    cursor.execute("UPDATE users SET wallet=? WHERE user_id=?", (wallet, user_id))
    conn.commit()

def set_investment(user_id, jumps, profit):
    cursor.execute("UPDATE users SET active_investment=?, pending_profit=? WHERE user_id=?", (jumps, profit, user_id))
    conn.commit()

def collect_profit(user_id):
    cursor.execute("SELECT pending_profit FROM users WHERE user_id=?", (user_id,))
    profit = cursor.fetchone()[0]
    cursor.execute("UPDATE users SET balance = balance + ?, pending_profit=0 WHERE user_id=?", (profit, user_id))
    conn.commit()
    return profit
