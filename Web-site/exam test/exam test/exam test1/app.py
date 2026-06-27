import re 
from flask import Flask, render_template, request, redirect, url_for, session, abort #for remember me 
from database.inloggen import show_inlog_Admin, show_clients,  check_user, get_user_profile, get_user_purchases
from database.register import add_user,user_exist, tableDo_if_not
from database.forget import init_db, check_user, reset_password_with_email
from database.products import get_all_products, tableProdDo_if_not, populate_products, add_to_cart, get_cart_items, get_cart_count, remove_from_cart, update_cart_quantity 
from database.profile import get_user_profile, update_user_field, update_wallet
from database.besteld_prod import process_checkout
from database.one_prod import get_product_by_id
from datetime import datetime
from collections import defaultdict
# Hashing passwords
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "super-secret-key-kiev-777"
tableDo_if_not()
tableProdDo_if_not()
populate_products()

def is_username_valid(username):
    errors = []
    if len(username) < 6:
        errors.append('length')
    if not re.search(r"[A-Z]", username):
        errors.append('capital')
    # Add other rules if needed
    is_valid = len(errors) == 0
    return is_valid, errors

def is_password_strong(password):
    errors = []
    if len(password) < 8:
        errors.append('length')
    if not re.search(r"[A-Z]", password):
        errors.append('capital')
    if not re.search(r"[0-9]", password):
        errors.append('number')
    if not re.search(r"[!@#$%^&*]", password):
        errors.append('special')
    return len(errors) == 0, errors

def is_email_valid(email):
    errors = []
    if len(email) < 16:
        errors.append('length')
    if not re.search(r"[!@#$%^&_()\|/\-\*]", email):
        errors.append('special')
    return len(errors) == 0, errors

@app.route("/register.html", methods=["GET", "POST"])
def register():
    general_error = None
    all_errors = {"email": [], "uname": [], "psw": []}

    if request.method == "POST":
        username = request.form.get("uname")
        email = request.form.get("gmail")
        password = request.form.get("psw")

        email_valid, all_errors["email"] = is_email_valid(email)
        uname_valid, all_errors["uname"] = is_username_valid(username)
        psw_valid, all_errors["psw"] = is_password_strong(password)

        if email_valid and uname_valid and psw_valid:
            if not user_exist(username, email): 
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                
                if add_user(username, email, hashed_password):
                    return redirect(url_for('inlogg'))
                else:
                    general_error = "Database error."
            else:
                # Specific "already exists" errors
                all_errors["email"].append("exist")
                all_errors["uname"].append("exist")
        
    return render_template("register.html", error=general_error, errors=all_errors)

@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/inloggen.html", methods = ["GET","POST"])
def inlogg():
    error = None
    if request.method == "POST":
        # get names
        username = request.form.get("uname")
        password = request.form.get("psw")
        remember = request.form.get("remember")

        # check if this user exist
        if check_user(username, password):
            #if we remember inlog then we do a session
            session.permanent = True if remember else False
            session["user"] = username #save username name

            return redirect(url_for('product'))
        else:
            error = "Invalid username or password!"

    return render_template("inloggen.html", error = error)





# @app.route("/register.html", methods = ["GET","POST"])
# def register():
#     general_error = None
#     # Dictionary to hold the error lists for each field
#     all_errors = {"email": [], "uname": [], "psw": []}

#     if request.method == "POST":
#         username = request.form.get("uname")
#         email = request.form.get("gmail")
#         password = request.form.get("psw")

#         # Run all three validations
#         email_valid, all_errors["email"] = is_email_valid(email)
#         uname_valid, all_errors["uname"] = is_username_valid(username)
#         psw_valid, all_errors["psw"] = is_password_strong(password)

#         # Check if everything is valid
#         if email_valid and uname_valid and psw_valid:
#             # Check if this user exists in DB (using your existing function)
#             if not check_user(username, email): 
#                 if add_user(username, email, password):
#                     return redirect(url_for('inlogg'))
#                 else:
#                     general_error = "Database error. Please try again."
#             else:
#                 # Add 'exist' code to specific fields if they are taken
#                 all_errors["email"].append("exist")
#                 all_errors["uname"].append("exist")
#         else:
#             # Some requirements weren't met
#             pass

#     return render_template("register.html", error=general_error, errors=all_errors)


@app.route("/logout")
def logout():
    session.clear() # all session cleaned
    return redirect(url_for('index'))

@app.context_processor
def inject_cart_count():
    count = 0
    if 'cart' in session:
        count = len(session['cart'])
    return dict(cart_count=count)

# @app.route("/product.html")
# def product():
# # 1. Get current filters from URL
#     active_filters = {
#         'category': request.args.get('category'),
#         'size': request.args.get('size'),
#         'brand': request.args.get('brand'),
#         'material': request.args.get('material'),
#         'sex': request.args.get('sex'),
#         'min_price': request.args.get('min_price', type=float),
#         'max_price': request.args.get('max_price', type=float)
#     }

#     # 2. Fetch products using the filters
#     items = get_all_products(
#         active_filters['category'], 
#         active_filters['size'], 
#         active_filters['brand'], 
#         active_filters['material'],
#         active_filters['sex'],
#         active_filters['min_price'],
#         active_filters['max_price']
#     )

#     # 3. Pass both the items AND the active filters to the page
#     return render_template("product.html", products=items, active=active_filters)

@app.route("/product") # Removed .html for a cleaner URL
def product():
    # Capture the search term
    search_term = request.args.get('search', '').strip()

    active_filters = {
        'category': request.args.get('category'),
        'size': request.args.get('size'),
        'brand': request.args.get('brand'),
        'material': request.args.get('material'),
        'sex': request.args.get('sex'),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float)
    }

    # Get items from DB
    items = get_all_products(
        category=active_filters['category'], 
        size=active_filters['size'], 
        brand=active_filters['brand'], 
        material=active_filters['material'],
        sex=active_filters['sex'],
        min_p=active_filters['min_price'],
        max_p=active_filters['max_price'],
        search_query=search_term
    )

    # You also need the cart count for the header badge
    cart_count = 0 
    if 'cart' in session:
        cart_count = len(session['cart'])

    return render_template("product.html", 
                           products=items, 
                           active=active_filters, 
                           search_term=search_term,
                           cart_count=cart_count)

@app.route("/aboutus.html")
def aboutus():
    
    return render_template("aboutus.html")

@app.route("/forgot_password.html", methods=['GET', 'POST'])
def forgot_password():
    general_error = None
    # Initialize error dictionary similar to your register route
    all_errors = {"email": [], "uname": [], "psw": []}

    if request.method == 'POST':
        username = request.form.get('uname')
        email = request.form.get('gmail')
        new_password = request.form.get('newpsw')

        # 1. Validate the strength of the new password
        # Assuming is_password_strong returns (bool, list_of_errors)
        psw_valid, all_errors["psw"] = is_password_strong(new_password)

        if psw_valid:

            hashed_newPassword = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
            # 2. If password is valid, check if user exists and update
            success = reset_password_with_email(username, email, hashed_newPassword)
            if success:
                return redirect(url_for('inlogg'))
            else:
                general_error = "Username and Gmail do not match our records."
        else:
            # If password validation fails, the template will show the specific psw errors
            general_error = "Please fix the password requirements below."
    
    return render_template("forgot_password.html", error=general_error, errors=all_errors)

# @app.route("/test.html")
# def test_page():
#     # 1. Get data from the database using functions
#     all_users = show_inlog_Admin()
#     all_clients = show_clients()

#     return render_template("test.html", users=all_users, clients=all_clients)

# @app.route("/test.html")
# def test_fill_db():
#     # 1. Guarantee the tables exist
#     tableProdDo_if_not()
    
#     # 2. Fire the population script
#     populate_products()
    
#     return "Database trigger fired! Check the VS Code terminal."

# -------------ALL BESTELLING-----------------
# Inject cart count into all templates automatically
@app.context_processor
def inject_cart_count():
    if "user" in session:
        return {'cart_count': get_cart_count(session["user"])}
    return {'cart_count': 0}

@app.route('/add_to_cart/<int:product_id>')
def add_item_to_cart(product_id): 
    if 'user' not in session:
        return redirect(url_for('inlogg'))
    
    # Call your database function
    add_to_cart(session['user'], product_id)
    return redirect(url_for('product'))

@app.route("/remove_from_cart/<int:cart_id>")
def remove_item(cart_id):
    remove_from_cart(cart_id)
    return redirect(url_for('bestelling'))

# --- Update Quantity Route ---
@app.route("/update_cart/<int:cart_id>", methods=['POST'])
def update_cart(cart_id):
    if "user" not in session:
        return redirect(url_for('inlogg'))
    
    # Get the value from the <input name="quantity">
    new_qty = request.form.get('quantity', type=int)
    
    if new_qty is not None:
        update_cart_quantity(cart_id, new_qty)
         
    return redirect(url_for('bestelling'))

# --- Cart Page Route ---
@app.route("/bestelling")
def bestelling():
    if "user" not in session:
        return redirect(url_for('inlogg'))
    
    items = get_cart_items(session["user"])
    subtotal = sum(item[2] * item[5] for item in items) 
    
    # Check if there is an error in the URL (like ?error=Insufficient balance)
    error = request.args.get('error')
    
    return render_template("bestelling.html", 
                           items=items, 
                           subtotal=subtotal, 
                           total=subtotal, 
                           error=error) # Pass error here

# @app.route("/bestelling.html")
# def bestelling():
#     if "user" not in session:
#         return redirect(url_for('inlogg'))
    
#     # Get only the orders for the logged-in user
#     user_orders = get_user_purchases(session["user"])
#     return render_template("bestelling.html", orders=user_orders)

@app.route("/logout", methods=["POST"], endpoint="checkout") 
def checkout():
    if "user" not in session:
        return redirect(url_for('inlogg'))

    # Call the logic from bestel_prod.py
    success, message = process_checkout(session["user"])
    
    if success:
        # Success: Go to profile
        return redirect(url_for('profile')) 
    else:
        # Failure: Go back to cart with the error (e.g., Insufficient balance)
        return redirect(url_for('bestelling', error=message))

# --------Profile------------
@app.route("/profile") # Use clean URL without .html
def profile():
    if "user" not in session:
        return redirect(url_for('inlogg'))
    
    user_data = get_user_profile(session["user"])
    edit_mode = request.args.get('edit') 
    
    return render_template("profile.html", user=user_data, edit_mode=edit_mode)

@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user" not in session:
        return redirect(url_for('inlogg'))

    old_username = session["user"]
    field = request.form.get("field")
    new_value = request.form.get("new_value")

    if new_value:
        # Update the database
        update_user_field(old_username, field, new_value)
        
        # If the user changed their username, update the session so they stay logged in
        if field == "username":
            session["user"] = new_value

    return redirect(url_for('profile'))

@app.route("/add_wallet", methods=["POST"])
def add_wallet():
    if "user" not in session:
        return redirect(url_for('inlogg'))
        
    amount = request.form.get("amount", type=float)
    if amount and amount > 0:
        update_wallet(session["user"], amount)
        
    return redirect(url_for('profile'))

# ----------Besteld---------
# @app.route('/besteld')
# def toon_bestellingen(): # Verander de naam hier naar iets unieks
#     if 'user' not in session:
#         return redirect(url_for('inlogg'))
    
#     username = session['user']
#     orders = get_grouped_purchases(username)
    
#     # Zorg dat je cart_count ergens vandaan haalt of op 0 laat
#     cart_count = 0 
    
#     return render_template('besteld.html', orders=orders, cart_count=cart_count)

@app.route('/one_prod/<int:id_product>')
def single_product(id_product):
    product = get_product_by_id(id_product)
    if product is None:
        return "Product not found", 404
    return render_template('one_prod.html', item=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST']) # Voeg POST toe
def add_item_to_cart_(product_id): 
    if 'user' not in session:
        return redirect(url_for('inlogg'))
    
    # Haal de gekozen maat op uit je dropdown
    selected_size = request.form.get('selected_size')
    
    if not selected_size:
        # Als er geen maat is, stuur ze terug naar het product
        return redirect(url_for('single_product', id_product=product_id))

    # Pas je database functie aan zodat hij ook de 'selected_size' opslaat
    add_to_cart(session['user'], product_id, selected_size)
    
    # Let op: 'product' moet de naam van je overzichtspagina-functie zijn
    return redirect(url_for('single_product', id_product=product_id))

if __name__ == "__main__":
    app.run(debug=True)



