import sqlite3

DB_NAME = "system_data.sqlite3"

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

def get_db_connection():
    # Do a connect with stabiel work with Flask
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # allow to communicate to rows not to indexs
    return conn

def init_db():
    """Создает таблицы, если они не существуют"""
    db = get_db_connection()
    cursor = db.cursor()
    
    # Table users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            wallet_balance REAL DEFAULT 0.0    
        )
    """)
    
    # Table boughts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id_purchase INTEGER PRIMARY KEY AUTOINCREMENT,
            id_inloggen INTEGER,
            purchase_item TEXT NOT NULL,
            amount_spent REAL NOT NULL,
            remaining_balance REAL NOT NULL,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_inloggen) REFERENCES users (id_user)
        )
    """)
    db.commit()
    db.close()

def check_user(username, password):
    """Check user exist"""
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE login = ?", (username,))
    user = cursor.fetchone()
    db.close()

    if user:
        return bcrypt.check_password_hash(user['password'],password)
    return False

def reset_password_with_email(username, email, new_password):
    """Update Password by verifying Username and Email"""
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # Check if both username AND email match a record
        cursor.execute("SELECT * FROM users WHERE login = ? AND email = ?", (username, email))
        user = cursor.fetchone()
        
        if user:
            cursor.execute("UPDATE users SET password = ? WHERE login = ?", (new_password, username))
            db.commit()
            return True
        return False 
    finally:
        db.close()

def show_inlog_Admin():
    """Returns all users"""
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    db.close()
    return rows

def show_clients_history():
    """Returns history all boughts clients"""
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id_purchase, u.login, p.purchase_item, p.amount_spent, p.date_time 
        FROM purchases p
        JOIN users u ON p.id_inloggen = u.id_user
    """)
    rows = cursor.fetchall()
    db.close()
    return rows