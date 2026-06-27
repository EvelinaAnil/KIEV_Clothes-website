import sqlite3

db = sqlite3.connect("system_data.sqlite3", check_same_thread=False)

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()


def tableDo_if_not():
    cursor = db.cursor()
    # for register in 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL, -- do also email
            password TEXT NOT NULL,
            wallet_balance REAL DEFAULT 0.0    
            )
    """)
    # to buy staff
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
                id_purchase INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,            -- Matches users(id_user)
                id_product INTEGER NOT NULL,         -- Needed to get the image/name
                quantity INTEGER NOT NULL,           -- Needed for the total
                amount_spent REAL NOT NULL,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_user) REFERENCES users (id_user),
                FOREIGN KEY (id_product) REFERENCES products (id_product)
            )
    """)
    db.commit()

    db.commit()

def add_user(username,email, password):
    """ Adds a new user to the database """
    try:
        cursor = db.cursor()
        # The 'login' column is UNIQUE, so this will fail if the name exists
        cursor.execute("INSERT INTO users (login,email, password) VALUES (?, ?, ?)", (username, email, password))
        db.commit()
        return True
    # except sqlite3.IntegrityError:
    #     # # This happens if the username/email already exists
    #     # return False
    except sqlite3.IntegrityError as e:
        # ---- ДОБАВЬ ЭТИ ДВЕ СТРОЧКИ НАПЕЧАТАТЬ ОШИБКУ В КОНСОЛЬ ----
        print("\n!!! СБОЙ ЗАПИСИ В БАЗУ ДАННЫХ !!!")
        print(f"Детали ошибки: {e}\n")
        # -----------------------------------------------------------
        return False
    
    

def user_exist(username, email):
    """ CHeck if exist this user or no """
    cursor = db.cursor()
    # Look for user
    cursor.execute("SELECT * FROM users WHERE login = ? OR email = ?", (username, email))
    user = cursor.fetchone()
    return cursor.fetchone() is not None
