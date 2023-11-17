from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_ORDERS, ORDERS_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, SHOPIFY_API_KEY
from airtable import Airtable
from datetime import datetime
import requests

# Creating a Blueprint for client routes
client_bp = Blueprint('client_bp', __name__)

# Initializing Airtable connection for clients
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtables_orders = Airtable(BASE_ID_ORDERS, ORDERS_TABLE, API_KEY)
airtable_strings = Airtable(BASE_ID_PRODUCTS, PRODUCTS_TABLE, API_KEY)

def get_shopify_headers():
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_API_KEY,
    }

def search_shopify_customer(email, first_name, last_name, city, zip):
    url = f"https://goatt-tennis.myshopify.com/admin/api/2023-04/customers/search.json?query=email:{email}"
    response = requests.get(url, headers=get_shopify_headers())
    if response.status_code == 200:
        customers = response.json().get('customers', [])
        if customers:
            customer_id = customers[0].get('id') 
            return customer_id
        else:
            print("Aucun client trouvé.")
            new_customer = create_shopify_customer(email, first_name, last_name, city, zip)
            return new_customer.get('id') if new_customer else None
    else:
        raise Exception(f"Failed to search customer: {response.text}")
    
def create_shopify_customer(email, first_name, last_name, city, zip):
    url = f"https://goatt-tennis.myshopify.com/admin/api/2021-01/customers.json"
    data = {
        "customer": {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        },
        "shipping_address": {
            "last_name": last_name,
            "first_name": first_name,
            "city": city,
            "country": "France",
            "zip": zip
        }
    }
    response = requests.post(url, json=data, headers=get_shopify_headers())
    return response.json().get('customer')

def create_draft_order(data):
    url = f"https://goatt-shopify.onrender.com/create_draft_order"

    lineItems = [{
        "variant_id": data['variant_id'],
        "requires_shipping": 'false',
        "quantity": data['quantité']
    },
     {
        "variant_id": '48665394905414',
        "requires_shipping": 'false',
        "quantity": data['quantité']
    },]

    draft_order_data = {
        "draft_order": {
            "line_items": lineItems,
            "customer": {
                "id": data['shopify_customer_id']
            },
            "shipping_address": {
                "address1": data['pickup_address'],
                "phone": data['phone'],
                "last_name": data['nom'],
                "first_name": data['prenom'],
                "city": data['pickup_town'],
                "country": "France",
                "zip": data['pickup_postal_code']
            },
            "shipping_line": {
                "custom": True,
                "price": data['price_delivery'],
                "title": 'Récupération et Livraison - ' + data['pose_type']
            },
        }
    }
    
    response = requests.post(url, json=draft_order_data, headers=get_shopify_headers())
    if response.status_code == 200:
        response_data = response.json()
        invoice_url = response_data['draft_order']['admin_graphql_api_id']
        order_id = invoice_url.split('/')[-1]
        return order_id
    else:
        return None 

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def complete_order(client_info, client_info_string=None):
    order_data = session.get('order_data', {})

    customer_id = search_shopify_customer(client_info['Email'], client_info['Prénom'], client_info['Nom'], client_info['Ville'], client_info['Code Postal'])
    
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
        'Téléphone': client_info['Téléphone'],
    })

    draft_order_info = {
        'variant_id': order_data['ShopifyVariantId'],
        'quantité': order_data['Quantité'],
        'shopify_customer_id': customer_id , 
        'pickup_address': order_data['Adresse de livraison'],
        'phone': client_info['Téléphone'],
        'nom': client_info['Nom'],
        'prenom': client_info['Prénom'],
        'pickup_town': client_info['Ville'],
        'pickup_postal_code': client_info['Code Postal'],
        'price_delivery': '5.99',
        'pose_type': 'Standard',
    }

    order_id = create_draft_order(draft_order_info)

    if order_id:
        order_data['Order_Id'] = order_id

    # Remove the 'ShopifyVariantId' key from order_data if it exists
    order_data.pop('ShopifyVariantId', None)

    # Remove the 'Quantité' key from order_data if it exists
    order_data.pop('Quantité', None)
    
    # Insert the complete order into the Airtable database
    airtables_orders.insert(order_data)

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
        'Téléphone': request.form['phonenumber'],
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