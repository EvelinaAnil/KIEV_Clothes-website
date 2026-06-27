import sqlite3

db = sqlite3.connect("system_data.sqlite3", check_same_thread=False)


    
# For testers to see if its works
def show_inlog_Admin():
    """Show data all Clients"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    return rows
#For testers tto see if thats works
def show_clients():
    """Show geshidenis all clients"""
    cursor = db.cursor()
    # use JOIN, so they were together ID
    cursor.execute("""
        SELECT p.id_purchase, u.login, p.purchase_item, p.amount_spent, p.date_time 
        FROM purchases p
        JOIN users u ON p.id_inloggen = u.id_user
    """)
    rows = cursor.fetchall()
    return rows

def check_user(username, password):
    """ CHeck if exist this user or no """
    cursor = db.cursor()
    # Look for user
    cursor.execute("SELECT * FROM users WHERE login = ? AND password = ?", (username,password))
    user = cursor.fetchone()

    if user:
        return True
    else:
        return False
    

def get_user_profile(username):
    """Fetch current user details for the info page"""
    cursor = db.cursor()
    # Adjust column names (e.g., login, gmail) to match your 'users' table
    cursor.execute("SELECT login, gmail FROM users WHERE login = ?", (username,))
    return cursor.fetchone()

def get_user_purchases(username):
    """Fetch orders for a specific user"""
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.purchase_item, p.amount_spent, p.date_time 
        FROM purchases p
        JOIN users u ON p.id_inloggen = u.id_user
        WHERE u.login = ?
    """, (username,))
    return cursor.fetchall()