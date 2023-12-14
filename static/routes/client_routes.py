from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from static.scripts.airtable import search_client, search_client_in_cordage, add_client

# Creating a Blueprint for client routes
client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/')
def page_nouveau_client():
    return render_template('page nouveau client.html')

@client_bp.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']

    # Search for string information by email in the strings table
    client_info_string = search_client_in_cordage(search_email)

    if client_info_string:
        client_info_string = client_info_string[0]['fields']
        session['client_info'] = client_info_string
        return jsonify({'found': True, 'client': client_info_string, 'cordage': client_info_string['Cordage'], 'tension': client_info_string['Tension'], 'phonenumber' : client_info_string['Téléphone']})
    else:
        client_info = search_client(search_email)
        if client_info:
            client_info = client_info[0]['fields']
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
