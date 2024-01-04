from flask import Blueprint, render_template, request, redirect, url_for, session
from static.scripts.shopify import search_shopify_customer, create_draft_order
from static.scripts.airtable import get_all_strings, get_all_orders, create_order
import re

# Creating a Blueprint for order routes
order_bp = Blueprint('order_bp', __name__)

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
        order_data['draft shopify id'] = int(order_id)
        session['draft_order_url'] = order_url

    # Remove the 'ShopifyVariantId' key from order_data if it exists
    order_data.pop('ShopifyVariantId', None)

    # Remove the 'Quantité' key from order_data if it exists
    order_data.pop('Quantité', None)

    # Remove the 'Ville' key from order_data if it exists
    order_data.pop('Ville', None)
    
    # Insert the complete order into the Airtable database
    create_order(order_data)

    # Clean up the session
    session.pop('order_data', None)
    return redirect(url_for('order_bp.order_confirmation'))

@order_bp.route('/')
def order_page():
    try:
        # Extract data from the database
        strings_response = get_all_strings()
        leads_response = get_all_orders()

        # Check if the response contains 'records'
        if 'records' in strings_response:
            strings_raw = strings_response['records']
        else:
            strings_raw = []

        if 'records' in leads_response:
            leads_raw = leads_response['records']
        else:
            leads_raw = []

        # Filter to keep only strings in stock and extract necessary info
        strings_info = {}
        for string in strings_raw:
            fields = string.get('fields', {})
            if fields.get('En stock'):
                string_name = fields.get('String', '')
                prix = fields.get('price', 0)
                shopify_variant_id = fields.get('Shopify variant id', '')
                strings_info[string_name] = {'prix': prix, 'shopify_variant_id': shopify_variant_id}

        emails = []
        for lead in leads_raw:
            fields = lead.get('fields', {})
            email = fields.get('Email', '')
            if email:
                emails.append(email)

        # Sort strings by brand in alphabetical order
        strings_info_sorted = dict(sorted(strings_info.items()))

        return render_template('order_page.html', strings_info=strings_info_sorted, emails=emails)

    except Exception as e:
        print("Error:", e)
        # Handle the exception or return an error message

@order_bp.route('/stringing_order', methods=['POST'])
def stringing_order():

    # Retrieve form data
    pickup_option = request.form['pickup_option']
    delivery_option = request.form['delivery_option']
    pickup_date = request.form['pickup_deposit_date']
    delivery_date = request.form['pickup_delivery_date']
    total_price_str = request.form['totalPrice']
    total_price_str = total_price_str.replace('€', '').strip()  
    total_price_str = total_price_str.replace(',', '.')
    total_price = float(total_price_str)
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
        'Prix': total_price,
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