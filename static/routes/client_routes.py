from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from static.scripts.airtable import search_client, search_client_in_cordage, add_client

# Creating a Blueprint for client routes
client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/')
def new_customer_page():
    return render_template('new_customer_page.html')

@client_bp.route('/search_client', methods=['POST'])
def search_client_route():
    search_email = request.form['search_email']

    # Search for client information by email in the cordage table
    client_info_string_response = search_client_in_cordage(search_email)
    client_info_string_records = client_info_string_response.get('records', [])

    if client_info_string_records:
        client_info_string = client_info_string_records[0]['fields']
        session['client_info'] = client_info_string
        return jsonify({'found': True, 'client': client_info_string, 'cordage': client_info_string.get('Cordage', ''), 'tension': client_info_string.get('Tension', ''), 'phonenumber' : client_info_string.get('Téléphone', '')})
    else:
        # Search for client information by email in the client table
        client_info_response = search_client(search_email)
        client_info_records = client_info_response.get('records', [])

        if client_info_records:
            client_info = client_info_records[0]['fields']
            session['client_info'] = client_info
            return jsonify({'found': True, 'client': client_info})
        
        return jsonify({'found': False, 'message': 'Aucun utilisateur trouvé avec cet email.'})
    
@client_bp.route('/add_client', methods=['POST'])
def add_client():

    # Retrieve the email entered in the form
    email = request.form['search_email']
    
    # Check if the user is already in the database
    existing_client = search_client(email)
    
    # If yes, then return to the home page
    if existing_client:
        flash("The user already exists in the database!", "failure")
        return redirect(url_for('client_bp.client'))
    
    # Create data to add to the database
    client_info = {
        'Nom': request.form['name'],
        'Prénom' : request.form['firstname'],
        'Email': request.form['search_email'],
        'Téléphone': request.form['phonenumber'],
    }

    add_client(client_info)

    session['client_info'] = client_info
    return redirect(url_for('order_bp.page_des_commandes_de_pose_cordage'))
