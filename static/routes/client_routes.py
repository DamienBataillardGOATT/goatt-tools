from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_ORDERS, ORDERS_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, SHOPIFY_API_KEY
from airtable import Airtable


# Creating a Blueprint for client routes
client_bp = Blueprint('client_bp', __name__)

# Initializing Airtable connection for clients
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtables_orders = Airtable(BASE_ID_ORDERS, ORDERS_TABLE, API_KEY)

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
            session['client_info'] = client_info
            session['client_info_string'] = client_info_string
            return redirect(url_for('order_bp.order'))
        else:
            session['client_info'] = client_info
            return redirect(url_for('order_bp.order'))
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
        'Téléphone': request.form['phonenumber'],
    }

    airtable_clients.insert(client_info)

    session['client_info'] = client_info
    return redirect(url_for('order_bp.order'))
