import sqlite3

def get_db_connection():
    # Make sure this matches your actual .db file name
    conn = sqlite3.connect('system_data.sqlite3')
    conn.row_factory = sqlite3.Row 
    return conn

def get_product_by_id(id_product):
    conn = get_db_connection()
    # fetchone() returns a single Row object or None
    product = conn.execute('SELECT * FROM products WHERE id_product = ?', (id_product,)).fetchone()
    conn.close()
    return product