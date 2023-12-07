from flask import Blueprint, render_template, request, redirect, url_for, session
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_ORDERS, ORDERS_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, SHOPIFY_API_KEY, ORDERS_TABLE_2
from airtable import Airtable
import requests
import re

# Creating a Blueprint for order routes
order_bp = Blueprint('order_bp', __name__)

# Initializing Airtable connection for products
airtable_strings = Airtable(BASE_ID_PRODUCTS, PRODUCTS_TABLE, API_KEY)
airtables_orders = Airtable(BASE_ID_ORDERS, ORDERS_TABLE, API_KEY)
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtable_cordarge = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)

def extract_postal_code_and_city(address):
    match = re.search(r'(\d{5})\s([A-Za-zÀ-ÿ\s-]+)$', address)
    if match:
        postal_code = match.group(1)
        city = match.group(2).strip()
        return postal_code, city
    else:
        return None, None
    
def extract_adress_street(adress):
    elements = adress.split()

    rue_et_numero = elements[:-2]

    adresse_raccourcie = ' '.join(rue_et_numero)
    return adresse_raccourcie

def get_shopify_headers():
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_API_KEY,
    }

def search_shopify_customer(email, first_name, last_name):
    url = f"https://goatt-prod.myshopify.com/admin/api/2023-04/customers/search.json?query=email:{email}"
    response = requests.get(url, headers=get_shopify_headers())
    if response.status_code == 200:
        customers = response.json().get('customers', [])
        print(customers)
        if customers:
            customer_id = customers[0].get('id') 
            return customer_id
        else:
            print("Aucun client trouvé.")
            new_customer = create_shopify_customer(email, first_name, last_name)
            return new_customer.get('id') if new_customer else None
    else:
        raise Exception(f"Failed to search customer: {response.text}")
    
def create_shopify_customer(email, first_name, last_name):
    url = f"https://goatt-tennis.myshopify.com/admin/api/2021-01/customers.json"
    data = {
        "customer": {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
    }
    response = requests.post(url, json=data, headers=get_shopify_headers())
    return response.json().get('customer')

def create_draft_order(data):
    url = f"https://goatt-shopify.onrender.com/create_draft_order_v2"

    lineItems = [{
        "variant_id": data['variant_id'],
        "requires_shipping": 'false',
        "quantity": data['quantité']
    },
     {
        "variant_id": '42066577457335',
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
        print(response_data)
        invoice_url = response_data['draft_order']['admin_graphql_api_id']
        order_id = invoice_url.split('/')[-1]
        order_url = f"https://goatt-prod.myshopify.com/store/goatt-tennis/draft_orders/{order_id}"
        return order_id, order_url
    else:
        return None 

def complete_order(order_data):
    client_info = session.get('client_info', {})

    if client_info :
        customer_id = search_shopify_customer(client_info['Email'], client_info['Prénom'], client_info['Nom'])
        email = client_info['Email']
        prenom = client_info['Prénom']
        nom = client_info['Nom']
        nom_complet = f"{client_info['Prénom']} {client_info['Nom']}"
        telephone = client_info['Téléphone']
    else :
        customer_id = search_shopify_customer(request.form['search_email'], request.form['firstname'], request.form['name'])
        email = request.form['search_email']
        prenom = request.form['firstname']
        nom = request.form['name']
        nom_complet = f"{request.form['firstname']} {request.form['name']}"
        telephone = request.form['phonenumber']
        
    order_data.update({
        'Email': email,
        'Nom complet': nom_complet,
        'Téléphone': telephone,
    })

    draft_order_info = {
        'variant_id': order_data['ShopifyVariantId'],
        'quantité': order_data['Quantité'],
        'shopify_customer_id': customer_id , 
        'pickup_address': order_data['Adresse de livraison'],
        'phone': telephone,
        'nom': nom,
        'prenom': prenom,
        'pickup_town': order_data['Ville'],
        'pickup_postal_code': order_data['Postcode'],
        'price_delivery': '5.99',
        'pose_type': 'Standard',
    }

    order_id, order_url = create_draft_order(draft_order_info)

    if order_id:
        order_data['draft shopify id'] = order_id
        session['draft_order_url'] = order_url

    # Remove the 'ShopifyVariantId' key from order_data if it exists
    order_data.pop('ShopifyVariantId', None)

    # Remove the 'Quantité' key from order_data if it exists
    order_data.pop('Quantité', None)

    # Remove the 'Ville' key from order_data if it exists
    order_data.pop('Ville', None)
    
    # Insert the complete order into the Airtable database
    airtables_orders.insert(order_data)

    # Clean up the session
    session.pop('order_data', None)
    return redirect(url_for('order_bp.order_confirmation'))

@order_bp.route('/')
def order():
    # Extract data from the database
    strings_raw = airtable_strings.get_all()
    leads_raw = airtable_cordarge.get_all()

    # Filter to keep only strings in stock and extract necessary info
    strings_info = {}
    for string in strings_raw:
        if string['fields'].get('En stock'):
            string_name = string['fields'].get('String', '')
            prix = string['fields'].get('price', 0)
            shopify_variant_id = string['fields'].get('Shopify variant id', '')
            strings_info[string_name] = {'prix': prix, 'shopify_variant_id': shopify_variant_id}


    emails = []
    for lead in leads_raw:
        email = lead['fields'].get('Email', '')
        if email:
            emails.append(email)

    # Sort strings by brand in alphabetical order
    strings_info_sorted = dict(sorted(strings_info.items()))
    
    return render_template('order.html', strings_info=strings_info_sorted, emails=emails)

@order_bp.route('/stringing_order', methods=['POST'])
def stringing_order():

    # Retrieve form data
    pickup_option = request.form['pickup_option']
    delivery_option = request.form['delivery_option']
    pickup_date = request.form['pickup_deposit_date']
    delivery_date = request.form['pickup_delivery_date']
    total_price = request.form['totalPrice']
    shopify_variant_id = request.form['shopifyVariantId']
    tension = request.form['Tension']
    quantity = request.form['string_quantity']
    
    # Initialize variables for addresses
    pickup_address = None
    delivery_address = None
    pickup_time = None
    delivery_time = None
    longitudeDeposit = None
    latitudeDeposit = None
    short_adress_pickup = None
    longitudeDelivery = None
    latitudeDelivery = None
    short_adress_delivery = None
    notes = request.form['client_notes']

    # Prepare data for pickup
    if pickup_option == 'address':
        pickup_address = request.form['pickup_address']
        pickup_time = request.form['selected_slot_deposit']
        longitudeDeposit = request.form['longitudeDeposit']
        latitudeDeposit = request.form['latitudeDeposit']
        short_adress_pickup = extract_adress_street(pickup_address)
        statut_recup = 'To Do'
    elif pickup_option == 'store':
        statut_recup = 'No Recup'

    # Prepare data for delivery
    if delivery_option == 'address':
        delivery_address = request.form['delivery_address']
        delivery_time = request.form['selected_slot_delivery']
        longitudeDelivery = request.form['longitudeDelivery']
        latitudeDelivery = request.form['latitudeDelivery']
        zip, city = extract_postal_code_and_city(delivery_address)
        short_adress_delivery = extract_adress_street(delivery_address)
        statut_livraison = 'To Do'
    elif delivery_option == 'store':
        statut_livraison =  'No Delivery'


    # Create a dictionary with the order data
    order_data = {
        'Type de commande': ['Cordage'],
        'Articles': request.form['searchInput'],
        'Quantities': request.form['string_quantity'],
        'Quantité': quantity,
        'Articles + Quantities': f"{request.form['string_quantity']}x {request.form['searchInput']}",
        'Tension': tension,
        'Cordage': request.form['searchInput'],
        '# raquettes': int(quantity),
        'Date de récupération': pickup_date,
        'Heure de récupération': int(pickup_time) if pickup_time else None,
        'Adresse de récupération': pickup_address if pickup_option == 'address' else None,
        'Date de livraison': delivery_date,
        'Heure de livraison': int(delivery_time) if delivery_time else None,
        'Adresse de livraison': delivery_address if delivery_option == 'address' else None,
        'Prix': float(total_price),
        'Statut récup' : statut_recup,
        'Statut livraison' : statut_livraison,
        'ShopifyVariantId': shopify_variant_id,
        'short pickup address': short_adress_pickup if short_adress_pickup else None,
        'Postcode': zip if delivery_option == 'address' else None,
        'Latitude Pickup Address': float(latitudeDeposit) if latitudeDeposit else None,
        'Longitude Pickup Address': float(longitudeDeposit) if longitudeDeposit else None,
        'Latitude Delivery Address': float(latitudeDelivery) if latitudeDelivery else None,
        'Longitude Delivery Address': float(longitudeDelivery) if longitudeDelivery else None,
        'short delivery address': short_adress_delivery if short_adress_delivery else None,
        'Ville': city if delivery_option == 'address' else None,
        'Notes': notes if notes else None 
    }

    complete_order(order_data)

    return redirect(url_for('order_bp.order_confirmation'))

@order_bp.route('/order_confirmation', methods=['GET'])
def order_confirmation():
    draft_order_url = session.get('draft_order_url', None)

    session.pop('draft_order_url', None)

    return render_template('order_confirmation.html', draft_order_url=draft_order_url)