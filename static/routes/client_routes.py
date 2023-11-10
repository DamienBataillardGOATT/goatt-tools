from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_ORDERS, ORDERS_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, ORDERS_TEST_TABLE
from airtable import Airtable
from datetime import datetime
import requests

# Creating a Blueprint for client routes
client_bp = Blueprint('client_bp', __name__)

# Initializing Airtable connection for clients
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtables_orders = Airtable(BASE_ID_ORDERS, ORDERS_TABLE, API_KEY)
airtable_strings = Airtable(BASE_ID_PRODUCTS, PRODUCTS_TABLE, API_KEY)
airtable_test_orders = Airtable(BASE_ID_ORDERS, ORDERS_TEST_TABLE, API_KEY)

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def send_draft_order_to_shopify(order_data):
    api_endpoint = 'https://goatt-shopify.onrender.com/create_draft_order'
    shopify_variant_id = order_data.get('ShopifyVariantId')
    quantity = order_data.get('Quantité', 1)

    line_items = [
        {
            "variant_id": shopify_variant_id,
            "quantity": quantity
        }
    ]

    order_payload = {
        "draft_order": {
            "line_items": line_items
        }
    }

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(api_endpoint, json=order_payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to create draft order", "status_code": response.status_code}

def complete_order(client_info, client_info_string=None):
    order_data = session.get('order_data', {})
    
    # Convert the birthdate into a datetime object to calculate age
    birthdate = datetime.strptime(client_info['Date de naissance'], '%Y-%m-%d')
    age = calculate_age(birthdate)

    # Using the informations from the last sale
    if client_info_string:
        # Retrieve the specific string price
        string_info = airtable_strings.search('String', client_info_string['Cordage'])
        if string_info:
            string_price = string_info[0]['fields']['price']
        else:
            string_price = 0  # or a default value if the string is not found
        
        # Calculate the total price
        quantity = int(order_data.get('Quantity', 1))
        total_price = string_price * quantity
        
        cordage = client_info_string['Cordage']
        tension = client_info_string['Tension']
        quantity = int(client_info_string.get('Quantité', 1))
        total_price = string_price * quantity

        # Update order_data with the informations from the last sale
        order_data.update({
            'Cordage': cordage,
            'Tension': tension,
            'Articles': f"{quantity}x {cordage}",
            'Prix': total_price,
        })

    # Add client information to order_data
    order_data.update({
        'Email': client_info['Email'],
        'Nom complet': f"{client_info['Prénom']} {client_info['Nom']}",
        'Date de naissance': client_info['Date de naissance'],
        'Age': age,
        'Sexe': client_info['Genre'],
    })

    print(order_data)

    # Send draft order to Shopify
    shopify_response = send_draft_order_to_shopify(order_data)
    print(shopify_response) 

    # Remove the 'ShopifyVariantId' key from order_data if it exists
    order_data.pop('ShopifyVariantId', None)

    # Remove the 'Quantité' key from order_data if it exists
    order_data.pop('Quantité', None)
    
    # Insert the complete order into the Airtable database
    airtable_test_orders.insert(order_data)

    # Clean up the session
    session.pop('order_data', None)
    return redirect(url_for('client_bp.order_confirmation'))

@client_bp.route('/')
def client():    
    return render_template('client.html')

@client_bp.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']

    # Search for the user by email in the clients table
    client_info = airtable_clients.search('Email', search_email)

    # Search for string information by email in the strings table
    client_info_string = airtables_orders.search('Email', search_email)
    
    if client_info:
        client_info = client_info[0]['fields']
        if client_info_string:
            client_info_string = client_info_string[0]['fields']
            complete_order(client_info, client_info_string)
            return redirect(url_for('client_bp.order_confirmation'))
        else:
            complete_order(client_info)
            return redirect(url_for('client_bp.order_confirmation'))
    else:
        flash('Aucun utilisateur trouvé avec cet email.', 'danger')
        return redirect(url_for('client_bp.client'))

@client_bp.route('/add_client', methods=['POST'])
def add_client():

    # Retrieve the email entered in the form
    email = request.form['email']
    
    # Check if the user is already in the database
    existing_client = airtable_clients.search('Email', email)
    
    # If yes, then return to the home page
    if existing_client:
        flash("The user already exists in the database!", "failure")
        return redirect(url_for('client_bp.client'))
    
    # Create data to add to the database
    client_info = {
        'Nom': request.form['name'],
        'Prénom' : request.form['firstname'],
        'Email': request.form['email'],
        'Ville': request.form['city'],
        'Code Postal': request.form['zip'],
        'Genre': request.form['genre'],
        'Date de naissance': request.form['birthdate']
    }

    airtable_clients.insert(client_info)

    complete_order(client_info)
    return redirect(url_for('client_bp.order_confirmation'))

@client_bp.route('/order_confirmation')
def order_confirmation():
    return "Merci pour votre commande!"