import sqlite3

db = sqlite3.connect("system_data.sqlite3", check_same_thread=False)

def tableProdDo_if_not():
    cursor = db.cursor()
    
    # 2. Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            size TEXT,
            brand TEXT,
            material TEXT,
            image_path TEXT,
            sex TEXT
        )
    """)

# 2. Cart Table (Temporary items before buying)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id_cart INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER,
            id_product INTEGER,
            quantity INTEGER DEFAULT 1,
            selected_size TEXT,
            FOREIGN KEY (id_user) REFERENCES users (id_user),
            FOREIGN KEY (id_product) REFERENCES products (id_product)
        )
    """)

    # 3. Purchases Table (History of orders)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id_purchase INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER,
            id_product INTEGER,
            quantity INTEGER,
            amount_spent REAL,
            date_time TEXT,
            FOREIGN KEY (id_user) REFERENCES users (id_user)
        )
    """)
    db.commit()

def get_all_products(category=None, size=None, brand=None, material=None, sex=None, min_p=None, max_p=None):
    cursor = db.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if size:
        query += " AND size = ?"
        params.append(size)
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if material:
        query += " AND material = ?"
        params.append(material)
    if sex:
        query += " AND sex = ?"
        params.append(sex)

    if min_p is not None:
        query += " AND price >= ?"
        params.append(min_p)
    if max_p is not None:
        query += " AND price <= ?"
        params.append(max_p)
        
    cursor.execute(query, params)
    return cursor.fetchall()

def get_user_orders(username):
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            p.date_time, 
            prod.name, 
            p.amount_spent, 
            prod.brand,
            prod.image_path
        FROM purchases p
        JOIN users u ON p.id_user = u.id_user
        JOIN products prod ON p.id_product = prod.id_product
        WHERE u.login = ?
        ORDER BY p.date_time DESC
    """, (username,))
    return cursor.fetchall()

def populate_products():
    cursor = db.cursor()
    
    # Check if the table is empty before inserting
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_products = [
            # --- Previous Items ---
            ('Sweatshirt Basic', 'Sweatshirt', 39.00, 'M', 'Kiev Brand', 'Cotton', 'images/sweatshirtbasic.jpg', 'Woman'),
            ('Wide Leg Jeans', 'Jeans', 45.90, 'L', 'Zara', 'Denim', 'images/widelegjeansmen.jpg', 'Man'),
            ('Oversized Tee', 'T-shirt', 19.99, 'S', 'Bershka', 'Polyester', 'images/oversizedteev.jpg', 'Woman'),
            ('Slim Fit Denim', 'Jeans', 55.00, 'M', 'Zara', 'Denim', 'images/slimfitdenimm.jpg', 'Man'),
            ('Streetwear Hoodie', 'Hoodie', 49.99, 'XL', 'Bershka', 'Cotton', 'images/streatwearv.jpg', 'Woman'),
            ('Cargo Pants', 'Trousers', 42.00, 'M', 'Kiev Brand', 'Polyester', 'images/cargopantsm.jpg', 'Man'),
            ('Baggy Utility Trousers', 'Trousers', 45.00, 'L', 'Kiev Brand', 'Cotton', 'images/utilitytrousersm.jpg', 'Man'),
            ('Oversized Cotton Tee', 'T-shirt', 29.99, 'S', 'Bershka', 'Cotton', 'images/oversizedteecottonv.jpg', 'Woman'),
            ('Relaxed Fit Chinos', 'Trousers', 38.50, 'M', 'Kiev Brand', 'Polyester', 'images/chinom.jpg', 'Man'),
            ('Vintage Wash Denim', 'Jeans', 55.00, 'L', 'Bershka', 'Denim', 'images/vintagewashdenimm.jpg', 'Woman'),
            ('Techwear Cargo', 'Trousers', 48.00, 'XL', 'Kiev Brand', 'Nylon', 'images/techwearm.jpg', 'Man'),

            # --- "M" Series (Man) ---
            ('Urban Relaxed Fit', 'Trousers', 44.00, 'L', 'Zara', 'Cotton', 'images/m.jpg', 'Man'),
            ('Casual Button Shirt', 'T-shirt', 29.00, 'M', 'Bershka', 'Cotton', 'images/m1.jpg', 'Man'),
            ('Grey Lounge Sweatshirt', 'Sweatshirt', 35.00, 'XL', 'Kiev Brand', 'Polyester', 'images/m2.jpg', 'Man'),
            ('Graphic Street Tee', 'T-shirt', 22.00, 'S', 'Adidas', 'Cotton', 'images/m3.jpg', 'Man'),
            ('V-Neck Essential', 'T-shirt', 18.50, 'M', 'Nike', 'Polyester', 'images/m4.jpg', 'Man'),
            ('Athletic Tank', 'T-shirt', 15.00, 'L', 'Adidas', 'Nylon', 'images/m5.jpg', 'Man'),

            # --- "W" Series (Woman) ---
            ('White Corset Top', 'T-shirt', 25.00, 'S', 'Bershka', 'Cotton', 'images/w1.jpg', 'Woman'),
            ('Mom Fit Denim', 'Jeans', 48.00, 'M', 'Zara', 'Denim', 'images/w2.jpg', 'Woman'),
            ('High Waist Trousers', 'Trousers', 52.00, 'L', 'Kiev Brand', 'Wool', 'images/w3.jpg', 'Woman'),
            ('Summer Shorts Set', 'T-shirt', 30.00, 'XS', 'Adidas', 'Polyester', 'images/w4.jpg', 'Woman'),
            ('Straight Leg Denim', 'Jeans', 45.00, 'M', 'Zara', 'Denim', 'images/w5.jpg', 'Woman'),
            ('Basic White Tee', 'T-shirt', 12.00, 'S', 'Nike', 'Cotton', 'images/w6.jpg', 'Woman'),
            ('Cozy Knit Hoodie', 'Hoodie', 59.00, 'XL', 'Bershka', 'Wool', 'images/w7.jpg', 'Woman'),
            ('Ribbed Crop Top', 'T-shirt', 19.00, 'XS', 'Zara', 'Cotton', 'images/w8.jpg', 'Woman'),
            ('Tailored Smart Trousers', 'Trousers', 65.00, 'M', 'Kiev Brand', 'Nylon', 'images/w9.jpg', 'Woman'),

            # --- "Heren" and "HH" Series ---
            ('Classic Overcoat', 'Trousers', 120.00, 'L', 'Zara', 'Wool', 'images/heren.jpg', 'Man'),
            ('Linen Blend Pants', 'Trousers', 55.00, 'M', 'Kiev Brand', 'Cotton', 'images/heren.2.jpg', 'Man'),
            ('Retro Sports Jacket', 'Sweatshirt', 75.00, 'XL', 'Adidas', 'Nylon', 'images/hh.jpg', 'Man'),
            ('Graphic Back Hoodie', 'Hoodie', 68.00, 'L', 'Nike', 'Cotton', 'images/hh1.jpg', 'Man'),
            ('Striped Knitwear', 'Sweatshirt', 49.00, 'M', 'Zara', 'Wool', 'images/hh2.jpg', 'Man'),
            ('Sleek Night Tee', 'T-shirt', 26.00, 'S', 'Bershka', 'Polyester', 'images/hh3.jpg', 'Man'),

            # --- Final Miscellaneous ---
            ('Streetwear Cargo', 'Trousers', 58.00, 'L', 'Nike', 'Nylon', 'images/tt1.jpg', 'Man'),
            ('Bucket Hat Combo Tee', 'T-shirt', 32.00, 'M', 'Kiev Brand', 'Cotton', 'images/tt2.jpg', 'Man'),
            ('Oversized Hoodie Pro', 'Hoodie', 85.00, 'XL', 'Nike', 'Polyester', 'images/pp.jpg', 'Man'),
            ('Utility Vest T-shirt', 'T-shirt', 40.00, 'L', 'Adidas', 'Nylon', 'images/qq1.jpg', 'Man')
        ]

        cursor.executemany("""
            INSERT INTO products (name, category, price, size, brand, material, image_path, sex)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_products)

        db.commit()


def add_to_cart(username, product_id, size=None): # size=None maakt het optioneel
    cursor = db.cursor()
    
    # 1. Haal de user_id op
    cursor.execute("SELECT id_user FROM users WHERE login = ?", (username,))
    user_row = cursor.fetchone()
    if not user_row: 
        return
    user_id = user_row[0]
    
    # 2. Als er GEEN size is meegegeven, haal de standaardmaat uit 'products'
    if size is None:
        cursor.execute("SELECT size FROM products WHERE id_product = ?", (product_id,))
        result = cursor.fetchone()
        size = result[0] if result else "Onbekend"

    # 3. Check of dit product MET DEZE MAAT al in de winkelwagen staat
    cursor.execute("""
        SELECT id_cart FROM cart 
        WHERE id_user = ? AND id_product = ? AND selected_size = ?
    """, (user_id, product_id, size))
    item = cursor.fetchone()
    
    if item:
        # Bestaat al? Verhoog aantal
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE id_cart = ?", (item[0],))
    else:
        # Nieuw? Toevoegen met de (gekozen of standaard) maat
        cursor.execute("""
            INSERT INTO cart (id_user, id_product, quantity, selected_size) 
            VALUES (?, ?, 1, ?)
        """, (user_id, product_id, size))
        
    db.commit()

# def add_to_cart(username, product_id):
#     cursor = db.cursor()
#     cursor.execute("SELECT id_user FROM users WHERE login = ?", (username,))
#     user_row = cursor.fetchone()
#     if not user_row: return
#     user_id = user_row[0]
    
#     # Get the default size of the product to store it in the cart
#     cursor.execute("SELECT size FROM products WHERE id_product = ?", (product_id,))
#     prod_size = cursor.fetchone()[0]
    
#     # Check if item is already in cart
#     cursor.execute("""
#         SELECT id_cart FROM cart 
#         WHERE id_user = ? AND id_product = ?
#     """, (user_id, product_id))
#     item = cursor.fetchone()
    
#     if item:
#         cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE id_cart = ?", (item[0],))
#     else:
#         cursor.execute("""
#             INSERT INTO cart (id_user, id_product, quantity, selected_size) 
#             VALUES (?, ?, 1, ?)
#         """, (user_id, product_id, prod_size))
#     db.commit()

# def add_to_cart(username, product_id, size):
#     cursor = db.cursor()
    
#     # 1. Haal de user_id op via de gebruikersnaam
#     cursor.execute("SELECT id_user FROM users WHERE login = ?", (username,))
#     user_row = cursor.fetchone()
#     if not user_row: 
#         return
#     user_id = user_row[0]
    
#     # 2. Check of dit product MET DEZE MAAT al in de winkelwagen staat
#     # Belangrijk: we checken nu op id_user AND id_product AND selected_size
#     cursor.execute("""
#         SELECT id_cart FROM cart 
#         WHERE id_user = ? AND id_product = ? AND selected_size = ?
#     """, (user_id, product_id, size))
#     item = cursor.fetchone()
    
#     if item:
#         # Als het exact hetzelfde item (maat + id) is: verhoog aantal
#         cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE id_cart = ?", (item[0],))
#     else:
#         # Als het een nieuwe maat of nieuw product is: voeg toe als nieuwe rij
#         cursor.execute("""
#             INSERT INTO cart (id_user, id_product, quantity, selected_size) 
#             VALUES (?, ?, 1, ?)
#         """, (user_id, product_id, size))
        
#     db.commit()


def get_cart_items(username):
    cursor = db.cursor()
    # Fixed the order and size selection
    cursor.execute("""
        SELECT 
            c.id_cart,      -- [0]
            p.name,         -- [1]
            p.price,        -- [2]
            p.brand,        -- [3]
            p.image_path,   -- [4]
            c.quantity,     -- [5]
            p.id_product,   -- [6]
            c.selected_size -- [7]
        FROM cart c
        JOIN users u ON c.id_user = u.id_user
        JOIN products p ON c.id_product = p.id_product
        WHERE u.login = ?
    """, (username,))
    return cursor.fetchall()


def get_cart_count(username):
    cursor = db.cursor()
    cursor.execute("SELECT SUM(quantity) FROM cart c JOIN users u ON c.id_user = u.id_user WHERE u.login = ?", (username,))
    result = cursor.fetchone()[0]
    return result if result else 0

def remove_from_cart(cart_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM cart WHERE id_cart = ?", (cart_id,))
    db.commit()

def update_cart_quantity(cart_id, new_qty):
    cursor = db.cursor()
    if new_qty > 0:
        cursor.execute("UPDATE cart SET quantity = ? WHERE id_cart = ?", (new_qty, cart_id))
    else:
        # If quantity is 0 or less, just remove the item
        cursor.execute("DELETE FROM cart WHERE id_cart = ?", (cart_id,))
    db.commit()



def get_all_products(category=None, size=None, brand=None, material=None, sex=None, min_p=None, max_p=None, search_query=None):
    cursor = db.cursor()
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR category LIKE ? OR brand LIKE ?)"
        s = f"%{search_query}%"
        params.extend([s, s, s])

    if category:
        query += " AND category = ?"
        params.append(category)
    if size:
        query += " AND size = ?"
        params.append(size)
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if material:
        query += " AND material = ?"
        params.append(material)
    if sex:
        query += " AND sex = ?"
        params.append(sex)
    if min_p is not None:
        query += " AND price >= ?"
        params.append(min_p)
    if max_p is not None:
        query += " AND price <= ?"
        params.append(max_p)

    cursor.execute(query, params)
    return cursor.fetchall()