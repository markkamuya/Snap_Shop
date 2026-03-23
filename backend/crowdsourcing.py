import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CRED_PATH  # Import the Firebase credentials path

# Initialize Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def add_pending_product(store, name, price, store_location, category, subcategory, description):
    try:
        # Reference to the 'pending_products' collection
        products_ref = db.collection('pending_products')

        # Ensure store_location is a Firestore GeoPoint (latitude, longitude)
        if isinstance(store_location, tuple) and len(store_location) == 2:
            geo_point = firestore.GeoPoint(store_location[0], store_location[1])
        else:
            raise ValueError("store_location must be a tuple of (latitude, longitude)")

        # Create a dictionary with the product data
        product_data = {
            'store': store,
            'name': name,
            'price': price,
            'storeLocation': geo_point,  # Firestore GeoPoint
            'category': category,
            'subcategory': subcategory,
            'description': description
        }

        # Add the product document to the collection
        products_ref.add(product_data)
        print("Product added to pending_products successfully!")

    except Exception as e:
        print(f"Error adding product: {str(e)}")

def get_pending_products():
    try:
        # Reference to the 'pending_products' collection
        products_ref = db.collection('pending_products')

        # Fetch all documents from the collection
        products = products_ref.stream()

        # Create a list to store products
        product_list = []
        for product in products:
            product_data = product.to_dict()
            product_data['id'] = product.id  # Adding the document ID to the result
            product_list.append(product_data)

        return product_list

    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return []