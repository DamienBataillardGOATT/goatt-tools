from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from static.routes.config import API_KEY, BASE_ID_PRODUCTS, PRODUCTS_TABLE
from airtable import Airtable

# Creating a Blueprint for order routes
order_bp = Blueprint('order_bp', __name__)

# Initializing Airtable connection for products
airtable_strings = Airtable(BASE_ID_PRODUCTS, PRODUCTS_TABLE, API_KEY)

@order_bp.route('/')
def order():
    # Extract data from the database
    strings_raw = airtable_strings.get_all()

    # Filter to keep only strings in stock and extract necessary info
    strings_info = {}
    for string in strings_raw:
        if string['fields'].get('En stock'):
            string_name = string['fields'].get('String', '')
            prix = string['fields'].get('price', 0)
            shopify_variant_id = string['fields'].get('Shopify variant id', '')
            strings_info[string_name] = {'prix': prix, 'shopify_variant_id': shopify_variant_id}

    # Sort strings by brand in alphabetical order
    strings_info_sorted = dict(sorted(strings_info.items()))
    
    return render_template('index.html', strings_info=strings_info_sorted)

@order_bp.route('/stringing_order', methods=['POST'])
def stringing_order():

    # Retrieve form data
    pickup_option = request.form['pickup_option']
    delivery_option = request.form['delivery_option']
    pickup_time = request.form['pickup_time']
    delivery_date = request.form['pickup_delivery_date']
    delivery_time = request.form['selected_slot']
    total_cart_price = request.form['totalCartPrice']
    shopify_variant_id = request.form['shopifyVariantId']
    
    # Initialize variables for addresses
    pickup_address = None
    delivery_address = None
    store_pickup_address = None
    store_delivery_address = None

    # Prepare data for pickup
    if pickup_option == 'address':
        pickup_address = request.form['pickup_address']
    elif pickup_option == 'store':
        store_pickup_address = request.form['store_pickup_address']  # Retrieve the address of the pickup store
    
    # Prepare data for delivery
    if delivery_option == 'address':
        delivery_address = request.form['delivery_address']
    elif delivery_option == 'store':
        store_delivery_address = request.form['store_delivery_address']  # Retrieve the address of the delivery store

    # Create a dictionary with the order data
    order_data = {
        'Articles': f"{request.form['string_quantity']}x {request.form['searchInput']}",
        'Quantité': request.form['string_quantity'],
        'ShopifyVariantId': shopify_variant_id,
        'Date de récupération': request.form['deposit_date'],
        'Heure de récupération': int(pickup_time),
        'Adresse de récupération': pickup_address if pickup_option == 'adresse' else store_pickup_address,
        'Date de livraison': delivery_date,
        'Heure de livraison': int(delivery_time),
        'Adresse de livraison': delivery_address if delivery_option == 'adresse' else store_delivery_address,
        'Prix': float(total_cart_price),
    }

    # Store the order data in the session to use after creating or retrieving the client
    session['order_data'] = order_data

    # Redirect to the client page to check if it's a new order or not
    return redirect(url_for('client_bp.client'))