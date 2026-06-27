import sqlite3
from datetime import datetime

def process_checkout(username):
    conn = sqlite3.connect('system_data.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Get user ID
        cursor.execute("SELECT id_user, wallet_balance FROM users WHERE login = ?", (username,))
        user = cursor.fetchone()
        if not user: return False, "User not found"
        user_id = user['id_user']
        
        # 2. Get all items in the user's cart
        cursor.execute("""
            SELECT c.id_product, c.quantity, p.price 
            FROM cart c 
            JOIN products p ON c.id_product = p.id_product 
            WHERE c.id_user = ?
        """, (user_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return False, "Cart is empty"
            
        # 3. Calculate total cost
        total_cost = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Optional: Check if user has enough money
        if user['wallet_balance'] < total_cost:
            return False, "Insufficient balance"

        # 4. Move items to purchases table
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in cart_items:
            cursor.execute("""
                    INSERT INTO purchases (id_user, id_product, quantity, amount_spent, date_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, item['id_product'], item['quantity'], item['price'] * item['quantity'], current_time))
        
        # 5. Deduct from wallet
        cursor.execute("UPDATE users SET wallet_balance = wallet_balance - ? WHERE id_user = ?", (total_cost, user_id))
        
        # 6. Clear the cart
        cursor.execute("DELETE FROM cart WHERE id_user = ?", (user_id,))
        
        conn.commit()
        return True, "Success"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


