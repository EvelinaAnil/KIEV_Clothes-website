import sqlite3



def get_db_connection():
    """Maakt een nieuwe verbinding aan voor elke actie"""
    conn = sqlite3.connect('system_data.sqlite3', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Hiermee kun je user['login'] gebruiken
    return conn

def get_user_profile(username):
    conn = get_db_connection() # OPEN verbinding
    cursor = conn.cursor()
    cursor.execute("SELECT id_user, login, email, password, wallet_balance FROM users WHERE login = ?", (username,))
    user = cursor.fetchone()
    conn.close() # SLUIT pas als je klaar bent
    return user

def update_user_field(old_username, field, new_value):
    conn = get_db_connection() # OPEN verbinding
    cursor = conn.cursor()
    if field == "username":
        cursor.execute("UPDATE users SET login = ? WHERE login = ?", (new_value, old_username))
    elif field == "email":
        cursor.execute("UPDATE users SET email = ? WHERE login = ?", (new_value, old_username))
    conn.commit()
    conn.close() # SLUIT pas als je klaar bent

def update_wallet(username, amount):
    conn = get_db_connection() # OPEN verbinding
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE login = ?", (amount, username))
    conn.commit()
    conn.close() # SLUIT pas als je klaar bent