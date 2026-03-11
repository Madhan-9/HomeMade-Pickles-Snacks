from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_12345'

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'

# File-based storage
USERS_FILE = 'users.json'
CARTS_FILE = 'carts.json'
ORDERS_FILE = 'orders.json'
PROFILES_FILE = 'profiles.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_carts():
    if os.path.exists(CARTS_FILE):
        with open(CARTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_carts(carts):
    with open(CARTS_FILE, 'w') as f:
        json.dump(carts, f)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f)

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f)

users = load_users()
user_carts = load_carts()
user_orders = load_orders()
user_profiles = load_profiles()

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        if user_id in users:
            user_data = users[user_id]
            return User(id=user_id, username=user_data['username'], email=user_data['email'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Products Data with details
product_details = {
    1: {'id': 1, 'name': 'Traditional Mango Pickle', 'category': 'veg-pickle', 'price': 299, 'oldPrice': 499, 'rating': 4.5, 'reviews': 1250, 'image': '../static/images/MangoPickel.jpg', 'badge': 'Best Seller', 'description': 'Aged to perfection with mustard seeds and aromatic spices. Our traditional mango pickle is made from the finest raw mangoes, sun-dried and blended with authentic Andhra spices.', 'weights': {'250': 150, '500': 280, '1000': 500}, 'discount': 40},
    2: {'id': 2, 'name': 'Lemon Pickle', 'category': 'veg-pickle', 'price': 199, 'oldPrice': 349, 'rating': 4.3, 'reviews': 890, 'image': '../static/images/Lemon pickel.jpg', 'badge': 'Popular', 'description': 'Tangy and spicy lemon pickle made with traditional recipe using fresh lemons and aromatic spices.', 'weights': {'250': 120, '500': 220, '1000': 400}, 'discount': 43},
    3: {'id': 3, 'name': 'Tomato Pickle', 'category': 'veg-pickle', 'price': 179, 'oldPrice': 299, 'rating': 4.2, 'reviews': 650, 'image': '../static/images/Tomato pickle.jpg', 'badge': 'New', 'description': 'Sweet and tangy tomato pickle with authentic flavors made from ripe tomatoes.', 'weights': {'250': 130, '500': 240, '1000': 450}, 'discount': 40},
    4: {'id': 4, 'name': 'Gongura Pickle', 'category': 'veg-pickle', 'price': 249, 'oldPrice': 399, 'rating': 4.6, 'reviews': 980, 'image': '../static/images/Gongura.jpg', 'badge': 'Special', 'description': 'Famous Andhra style gongura with fiery spices made from fresh sorrel leaves.', 'weights': {'250': 130, '500': 240, '1000': 450}, 'discount': 38},
    5: {'id': 5, 'name': 'Pandu Mirchi Pickle', 'category': 'veg-pickle', 'price': 189, 'oldPrice': 299, 'rating': 4.4, 'reviews': 720, 'image': '../static/images/pandu mirchi.jpg', 'badge': 'Hot', 'description': 'Spicy red chili pickle for spice lovers made from premium quality red chilies.', 'weights': {'250': 130, '500': 240, '1000': 450}, 'discount': 37},
    6: {'id': 6, 'name': 'Mixed Veg Pickle', 'category': 'veg-pickle', 'price': 349, 'oldPrice': 549, 'rating': 4.1, 'reviews': 450, 'image': '../static/images/Chekka Pakodi.jpg', 'description': 'Assorted vegetables pickled in aromatic spices with traditional recipe.', 'weights': {'250': 150, '500': 280, '1000': 500}, 'discount': 36},
    7: {'id': 7, 'name': 'Chicken Boneless Pickle', 'category': 'non-veg-pickle', 'price': 499, 'oldPrice': 799, 'rating': 4.7, 'reviews': 1560, 'image': '../static/images/chicken-boneless-pickle.jpg', 'badge': 'Favorite', 'description': 'Tender chicken pieces in spicy gravy made with authentic spices and cooking traditions.', 'weights': {'250': 600, '500': 1200, '1000': 1800}, 'discount': 38},
    8: {'id': 8, 'name': 'Fish Pickle', 'category': 'non-veg-pickle', 'price': 449, 'oldPrice': 699, 'rating': 4.5, 'reviews': 1120, 'image': '../static/images/fish pickle.JPG', 'description': 'Fisher fish pickle with coastal spices made from fresh fish and aromatic masala.', 'weights': {'250': 200, '500': 400, '1000': 800}, 'discount': 36},
    9: {'id': 9, 'name': 'Mutton Pickle', 'category': 'non-veg-pickle', 'price': 599, 'oldPrice': 999, 'rating': 4.8, 'reviews': 780, 'image': '../static/images/mutton pickle.jpg', 'badge': 'Premium', 'description': 'Rich and flavorful mutton pickle made with tender mutton pieces and exotic spices.', 'weights': {'250': 400, '500': 800, '1000': 1600}, 'discount': 40},
    10: {'id': 10, 'name': 'Gongura Chicken', 'category': 'non-veg-pickle', 'price': 449, 'oldPrice': 699, 'rating': 4.6, 'reviews': 920, 'image': '../static/images/gongurachicken.jpg', 'description': 'Spicy gongura chicken with authentic taste made with fresh gongura leaves.', 'weights': {'250': 350, '500': 700, '1000': 1050}, 'discount': 36},
    11: {'id': 11, 'name': 'Prawns Gongura', 'category': 'non-veg-pickle', 'price': 549, 'oldPrice': 899, 'rating': 4.4, 'reviews': 540, 'image': '../static/images/prawns_gongura.jpg', 'description': 'Juicy prawns with tangy gongura leaves cooked in authentic coastal style.', 'weights': {'250': 350, '500': 700, '1000': 1050}, 'discount': 39},
    12: {'id': 12, 'name': 'Gongura Mutton', 'category': 'non-veg-pickle', 'price': 649, 'oldPrice': 1049, 'rating': 4.7, 'reviews': 680, 'image': '../static/images/GonguraMutton-1.jpg', 'badge': 'Special', 'description': 'Mutton cooked with gongura and spices, a delicous Andhra specialty.', 'weights': {'250': 400, '500': 800, '1000': 1600}, 'discount': 38},
    13: {'id': 13, 'name': 'Aam Papad', 'category': 'snacks', 'price': 149, 'oldPrice': 249, 'rating': 4.3, 'reviews': 1890, 'image': '../static/images/Aam-Papad.jpg', 'badge': 'Kids Favorite', 'description': 'Sweet & tangy mango leather, sun-dried and made from pure mango pulp.', 'weights': {'250': 150, '500': 300, '1000': 600}, 'discount': 40},
    14: {'id': 14, 'name': 'Banana Chips', 'category': 'snacks', 'price': 129, 'oldPrice': 199, 'rating': 4.2, 'reviews': 1450, 'image': '../static/images/Banana1.jpg', 'description': 'Crispy and crunchy banana chips made from fresh bananas.', 'weights': {'250': 300, '500': 600, '1000': 800}, 'discount': 35},
    15: {'id': 15, 'name': 'Boondi Laddu', 'category': 'snacks', 'price': 249, 'oldPrice': 399, 'rating': 4.5, 'reviews': 980, 'image': '../static/images/boondi-laddu-665537.jpg', 'description': 'Traditional sweet balls with boondi made with fresh ingredients.', 'weights': {'250': 350, '500': 700, '1000': 1000}, 'discount': 38},
    16: {'id': 16, 'name': 'Sunnundalu', 'category': 'snacks', 'price': 199, 'oldPrice': 329, 'rating': 4.4, 'reviews': 650, 'image': '../static/images/Sunnundalu.jpg', 'description': 'Urud dal laddus from Andhra made with premium urad dal.', 'weights': {'250': 350, '500': 700, '1000': 1000}, 'discount': 40},
    17: {'id': 17, 'name': 'Rava Ladoo', 'category': 'snacks', 'price': 229, 'oldPrice': 349, 'rating': 4.3, 'reviews': 820, 'image': '../static/images/rava-ladoo-featured.jpg', 'description': 'Semolina balls with ghee and nuts, a traditional sweet delicacy.', 'weights': {'250': 300, '500': 600, '1000': 900}, 'discount': 34},
    18: {'id': 18, 'name': 'Kaju Chikki', 'category': 'snacks', 'price': 299, 'oldPrice': 499, 'rating': 4.6, 'reviews': 720, 'image': '../static/images/kaju-chikki.jpg', 'description': 'Cashew nut fudge with jaggery, a rich and delicious sweet.', 'weights': {'250': 250, '500': 500, '1000': 750}, 'discount': 40},
    19: {'id': 19, 'name': 'Peanut Chikki', 'category': 'snacks', 'price': 149, 'oldPrice': 249, 'rating': 4.2, 'reviews': 1650, 'image': '../static/images/peanutchikki_new_2048x.jpg', 'description': 'Crispy peanut candy made with roasted peanuts and jaggery.', 'weights': {'250': 200, '500': 400, '1000': 600}, 'discount': 40},
    20: {'id': 20, 'name': 'Gavvalu', 'category': 'snacks', 'price': 179, 'oldPrice': 299, 'rating': 4.1, 'reviews': 480, 'image': '../static/images/gavvalu_sweet.jpg', 'description': 'Sweet disk-shaped snacks from Andhra, crispy and delicious.', 'weights': {'250': 200, '500': 400, '1000': 600}, 'discount': 40},
}

products = {
    'non_veg_pickles': [
        {'id': 1, 'name': 'Chicken Pickle', 'weights': {'250': 600, '500': 1200, '1000': 1800}},
        {'id': 2, 'name': 'Fish Pickle', 'weights': {'250': 200, '500': 400, '1000': 800}},
        {'id': 3, 'name': 'Gongura Mutton', 'weights': {'250': 400, '500': 800, '1000': 1600}},
        {'id': 4, 'name': 'Mutton Pickle', 'weights': {'250': 400, '500': 800, '1000': 1600}},
        {'id': 5, 'name': 'Gongura Prawns', 'weights': {'250': 600, '500': 1200, '1000': 1800}},
        {'id': 6, 'name': 'Chicken Pickle (Gongura)', 'weights': {'250': 350, '500': 700, '1000': 1050}}
    ],
    'veg_pickles': [
        {'id': 7, 'name': 'Traditional Mango Pickle', 'weights': {'250': 150, '500': 280, '1000': 500}},
        {'id': 8, 'name': 'Zesty Lemon Pickle', 'weights': {'250': 120, '500': 220, '1000': 400}},
        {'id': 9, 'name': 'Tomato Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 10, 'name': 'Kakarakaya Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 11, 'name': 'Chintakaya Pickle', 'weights': {'250': 130, '500': 240, '1000': 450}},
        {'id': 12, 'name': 'Spicy Pandu Mirchi', 'weights': {'250': 130, '500': 240, '1000': 450}}
    ],
    'snacks': [
        {'id': 13, 'name': 'Banana Chips', 'weights': {'250': 300, '500': 600, '1000': 800}},
        {'id': 14, 'name': 'Crispy Aam-Papad', 'weights': {'250': 150, '500': 300, '1000': 600}},
        {'id': 15, 'name': 'Crispy Chekka Pakodi', 'weights': {'250': 50, '500': 100, '1000': 200}},
        {'id': 16, 'name': 'Boondhi Acchu', 'weights': {'250': 300, '500': 600, '1000': 900}},
        {'id': 17, 'name': 'Chekkalu', 'weights': {'250': 350, '500': 700, '1000': 1000}},
        {'id': 18, 'name': 'Ragi Laddu', 'weights': {'250': 350, '500': 700, '1000': 1000}},
        {'id': 19, 'name': 'Dry Fruit Laddu', 'weights': {'250': 500, '500': 1000, '1000': 1500}},
        {'id': 20, 'name': 'Kara Boondi', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 21, 'name': 'Gavvalu', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 22, 'name': 'Kaju Chikki', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 23, 'name': 'PeaNut Chikki', 'weights': {'250': 250, '500': 500, '1000': 750}},
        {'id': 24, 'name': 'Rava Laddu', 'weights': {'250': 250, '500': 500, '1000': 750}}
    ]
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    """Product detail page with weight selection"""
    product = product_details.get(product_id)
    if not product:
        return redirect(url_for('index'))
    
    # Get first weight for default selection
    first_weight = list(product['weights'].keys())[0]
    first_price = product['weights'][first_weight]
    
    # Get all products for related products
    all_products = list(product_details.values())
    return render_template('product_detail.html', product=product, all_products=all_products, first_weight=first_weight, first_price=first_price)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            user_data = users[username]
            if check_password_hash(user_data['password'], password):
                user = User(id=username, username=username, email=user_data['email'])
                login_user(user, remember=True)
                
                if username not in user_carts:
                    user_carts[username] = []
                    save_carts(user_carts)
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid password')
        else:
            return render_template('login.html', error='User not found')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if username in users:
            return render_template('signup.html', error='Username already exists')

        hashed_password = generate_password_hash(password)
        users[username] = {
            'username': username,
            'email': email,
            'password': hashed_password
        }
        save_users(users)
        
        user_carts[username] = []
        save_carts(user_carts)

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/non_veg_pickles')
@login_required
def non_veg_pickles():
    return render_template('non_veg_pickles.html', products=products['non_veg_pickles'])

@app.route('/veg_pickles')
@login_required
def veg_pickles():
    return render_template('veg_pickles.html', products=products['veg_pickles'])

@app.route('/snacks')
@login_required
def snacks():
    return render_template('snacks.html', products=products['snacks'])

@app.route('/cart')
@login_required
def cart():
    cart_items = user_carts.get(current_user.username, [])
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    price = data.get('price')
    quantity = data.get('quantity', 1)
    image = data.get('image')

    cart = user_carts.get(current_user.username, [])
    
    found = False
    for item in cart:
        if item.get('id') == product_id:
            item['quantity'] = item.get('quantity', 1) + quantity
            found = True
            break
    
    if not found:
        cart.append({
            'id': product_id,
            'name': product_name,
            'price': price,
            'quantity': quantity,
            'image': image
        })
    
    user_carts[current_user.username] = cart
    save_carts(user_carts)
    
    return {'success': True, 'message': 'Item added to cart', 'cart_count': sum(item.get('quantity', 1) for item in cart)}

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')

    cart = user_carts.get(current_user.username, [])
    cart = [item for item in cart if item.get('id') != product_id]
    user_carts[current_user.username] = cart
    save_carts(user_carts)
    
    return {'success': True, 'message': 'Item removed from cart', 'cart_count': sum(item.get('quantity', 1) for item in cart), 'cart': cart}

@app.route('/get_cart_count')
@login_required
def get_cart_count():
    cart = user_carts.get(current_user.username, [])
    return {'count': sum(item.get('quantity', 1) for item in cart)}

@app.route('/get_cart')
@login_required
def get_cart():
    cart = user_carts.get(current_user.username, [])
    return {'cart': cart}

@app.route('/update_cart_quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    data = request.get_json()
    product_id = data.get('product_id')
    change = data.get('change', 1)

    cart = user_carts.get(current_user.username, [])
    
    for item in cart:
        if item.get('id') == product_id:
            item['quantity'] = max(1, item.get('quantity', 1) + change)
            break
    
    user_carts[current_user.username] = cart
    save_carts(user_carts)
    
    return {'success': True, 'cart': cart, 'cart_count': sum(item.get('quantity', 1) for item in cart)}

@app.route('/check_login')
def check_login():
    if current_user.is_authenticated:
        return {'is_authenticated': True}
    return {'is_authenticated': False}

@app.route('/buy_now', methods=['POST'])
@login_required
def buy_now():
    """Direct buy without adding to cart - goes directly to checkout"""
    data = request.get_json()
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    price = data.get('price')
    quantity = data.get('quantity', 1)
    image = data.get('image')
    
    # Clear existing cart and add only this product for direct checkout
    cart = [{
        'id': product_id,
        'name': product_name,
        'price': price,
        'quantity': quantity,
        'image': image
    }]
    
    user_carts[current_user.username] = cart
    save_carts(user_carts)
    
    return {'success': True, 'message': 'Proceeding to checkout', 'redirect_url': url_for('checkout')}

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Try to get cart from form data first, then fall back to server cart
    cart_data = request.form.get('cart_data')
    if cart_data:
        try:
            cart_items = json.loads(cart_data)
            # Save to server cart for consistency
            user_carts[current_user.username] = cart_items
            save_carts(user_carts)
        except:
            cart_items = user_carts.get(current_user.username, [])
    else:
        cart_items = user_carts.get(current_user.username, [])

    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        payment_method = request.form.get('payment', '').strip()
        
        if not all([name, address, phone, payment_method]):
            return render_template('checkout.html', error="All fields are required.", cart_items=cart_items)

        if not phone.isdigit() or len(phone) != 10:
            return render_template('checkout.html', error="Phone number must be exactly 10 digits.", cart_items=cart_items)

        total_amount = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart_items)
        
        # Create order before clearing cart
        import time
        order_id = f"ORD-{int(time.time())}"
        order = {
            'order_id': order_id,
            'order_items': cart_items,
            'total_amount': total_amount,
            'name': name,
            'address': address,
            'phone': phone,
            'payment_method': payment_method,
            'status': 'Confirmed',
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save order to user orders
        if current_user.username not in user_orders:
            user_orders[current_user.username] = []
        user_orders[current_user.username].append(order)
        save_orders(user_orders)
        
        # Clear cart after order is saved
        user_carts[current_user.username] = []
        save_carts(user_carts)

        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('sucess', order_id=order_id))

    return render_template('checkout.html', cart_items=cart_items)

@app.route('/my_orders')
@login_required
def my_orders():
    """View all orders for the current user"""
    orders = user_orders.get(current_user.username, [])
    return render_template('my_orders.html', orders=orders)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile with details and order history"""
    user_profile = user_profiles.get(current_user.username, {})
    orders = user_orders.get(current_user.username, [])
    
    if request.method == 'POST':
        # Save or update profile
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        
        user_profiles[current_user.username] = {
            'full_name': full_name,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode
        }
        save_profiles(user_profiles)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', profile=user_profile, orders=orders, username=current_user.username)

@app.route('/sucess')
@login_required
def sucess():
    order_id = request.args.get('order_id', '')
    return render_template('sucess.html', order_id=order_id)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact us.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

