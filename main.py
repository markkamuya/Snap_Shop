import os

from openai import OpenAI
from openai._exceptions import OpenAIError
import firebase_admin
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_from_directory
from firebase_admin import credentials, firestore, auth
from flask_mail import Mail
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from backend.products import search_products

# Initialize Flask app
app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')  # Update for production
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# Signup Form
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

def parse_location(store_location):
    # Assuming store_location is a GeoPoint object
    if store_location:
        # Access latitude and longitude directly from GeoPoint
        return store_location.latitude, store_location.longitude
    return None  # If the location is not available

# Extract product names using OpenAI GPT-3/4
def clean_user_input(user_input):
    """Use OpenAI's GPT-3/4 to extract product names from noisy input"""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", 
                    "content": """You are a helpful assistant that can identify product names from noisy user input. 
                    Please extract the product names from the given input, even if they are misspelled or include extraneous words. 
                    You should ignore words like 'buy', 'cheap', 'deal', etc., and focus only on the product names.
                    For example:
                    - 'I need some milks please!' -> 'milk'
                    - 'Can you tell me where to get choclates or cmilks?' -> 'chocolate, milk'
                    """
                },
                {
                    "role": "user", 
                    "content": f"Extract the list of product names from the following input: {user_input}. Ignore irrelevant words like brands or adjectives, and focus on product names."
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        extracted_products = response.choices[0].message.content.strip().split(',')
        extracted_products = [product.strip().lower() for product in extracted_products]
        return extracted_products
    except OpenAIError as e:
        print(f"Error with OpenAI API: {e}")
        return []

# Retrieve products from Firestore
def get_product_data_from_firestore():
    products_ref = db.collection('products')  # 'products' is the name of the collection
    products = products_ref.stream()
    product_list = []
    for product in products:
        product_list.append(product.to_dict())
        #print("Product Data from Firestore:", product.to_dict())
    return product_list
def is_valid_price(price):
    try:
        # Try to convert price to float
        float(price)
        return True
    except ValueError:
        # Return False if conversion fails
        return False

@app.route("/find_cheapest_store", methods=["POST"])
def find_cheapest_store():
    # Get the input data from the request
    data = request.json
    user_input = data.get('product')  # Product name or search term
    radius = data.get("radius")  # Radius for location-based search (if needed)

    # Clean the user input to ensure it's in a valid format
    cleaned_products = clean_user_input(user_input)

    if not cleaned_products:
        return jsonify({"error": "No valid products identified in the input."}), 400

    # Call the function to search products on eBay and Amazon
    products = search_products(cleaned_products, entries_per_page=5, page_number=1)

    print(f"Producteeeeee:{products}")
    # Filter out any None values or invalid products (e.g., missing price)
    valid_products = []

    # Check all the products for valid price and rating, e.g. 'cheapest_ebay', 'cheapest_amazon', etc.
    for key, product in products.items():
        if product and product.get('price') is not None and is_valid_price(product['price']):
            valid_products.append(product)

    if not valid_products:
        return jsonify({"error": "No valid products found with a price."}), 400

    # Find the cheapest product (based on price)
    cheapest_product = min(valid_products, key=lambda x: float(x['price']))

    # Find the highest-rated product (based on rating)
    highest_rated_product = max(valid_products, key=lambda x: float(x['rating']) if x.get('rating') not in ["No rating", "No ratings available"] else 0)

    # Prepare the response to return both the cheapest and highest-rated products
    response = {
        "products": valid_products,  # Return all valid products in the response
        "cheapest_product": cheapest_product,  # The cheapest product
        "highest_rated_product": highest_rated_product  # The highest-rated product
    }

    return jsonify(response)

# SignUp Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = auth.create_user(
                email=form.email.data,
                password=form.password.data,
                display_name=form.username.data
            )
            db.collection('users').add({
                'username': form.username.data,
                'email': form.email.data,
                'firebase_uid': user.uid
            })
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('signup'))
    return render_template('signup.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = auth.get_user_by_email(form.email.data)
            session['user_id'] = user.uid
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('login.html', form=form)

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return 'Welcome to your dashboard!'

# Crowdsourcing Route to add products to Firestore
@app.route('/crowdsourcing', methods=['GET', 'POST'])
def crowdsourcing():
    if request.method == 'POST':
        data = request.get_json()

        # Basic validation
        required_fields = ['category', 'subcategory', 'name', 'store', 'price', 'description', 'storeLocation']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Field '{field}' is required."}), 400

        try:
            # Convert store_location_input to GeoPoint
            lat, lng = map(float, data['storeLocation'].strip("()").split(","))
            store_location = firestore.GeoPoint(lat, lng)

            # Reference to Firestore collection "pending_products"
            products_ref = db.collection('pending_products')

            # Add product data to Firestore
            data['storeLocation'] = store_location  # Use GeoPoint here
            products_ref.add(data)

            return jsonify({"message": "Data received and stored successfully!"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return send_from_directory(os.getcwd(), 'crowdsourcing.html')

# Serve the homepage
@app.route('/')
def home():
    return send_from_directory(os.getcwd(), 'frontend/homepage.html')  # Serve homepage.html

# Serve index
@app.route('/index')
def index():
    return send_from_directory(os.getcwd(), 'frontend/index.html')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.getcwd(), 'frontend/sitemap.xml') 

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
