from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_COMMANDES, COMMANDES_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, COMMANDES_TEST_TABLE
from airtable import Airtable
from datetime import datetime

# Création d'un Blueprint pour les routes client
client_bp = Blueprint('client_bp', __name__)

# Initialisation de la connexion Airtable pour les clients
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtables_commandes = Airtable(BASE_ID_COMMANDES, COMMANDES_TABLE, API_KEY)
airtable_cordages = Airtable(BASE_ID_PRODUCTS,PRODUCTS_TABLE, API_KEY)
airtable_test_commandes = Airtable(BASE_ID_COMMANDES, COMMANDES_TEST_TABLE, API_KEY)

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def complete_order(client_info):
    order_data = session.get('order_data', {})
    
    # Convertissez la date de naissance en objet datetime pour calculer l'âge
    birthdate = datetime.strptime(client_info['Date de naissance'], '%Y-%m-%d')
    age = calculate_age(birthdate)

    # Récupérez le prix du cordage spécifique
    cordage_info = airtable_cordages.search('String', client_info['Cordage'])
    if cordage_info:
        prix_cordage = cordage_info[0]['fields']['price']
    else:
        prix_cordage = 0  # ou une valeur par défaut si le cordage n'est pas trouvé

    # Calculez le prix total
    quantite = int(order_data.get('Quantité', 1))
    prix_total = prix_cordage * quantite
    
    # Ajoutez les informations du client à order_data
    order_data.update({
        'Email': client_info['Email'],
        'Nom complet': f"{client_info['Prénom']} {client_info['Nom']}",
        'Date de naissance': client_info['Date de naissance'],
        'Age': age,
        'Sexe': client_info['Genre'],
        'Cordage': client_info['Cordage'],
        'Tension': client_info['Tension'],
        'Articles': f"{order_data['Quantité']}x {client_info['Cordage']}",
        'Prix': prix_total,
    })

    print(order_data)

    # Supprimez la clé 'Quantité' de order_data si elle existe
    order_data.pop('Quantité', None)
    
    # Insérez la commande complète dans la base de données Airtable
    airtable_test_commandes.insert(order_data)

    # Nettoyez la session
    session.pop('order_data', None)
    return redirect(url_for('client_bp.order_confirmation'))

@client_bp.route('/')
def client():    
    return render_template('client.html')

@client_bp.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']

    # Recherchez l'utilisateur par e-mail dans la table des clients
    client_info = airtable_clients.search('Email', search_email)

    # Recherchez les informations de cordage par e-mail dans la table des cordages
    client_info_cordage = airtables_commandes.search('Email', search_email)
    
    if client_info:
        client_info = client_info[0]['fields']
        if client_info_cordage:
            client_info_cordage = client_info_cordage[0]['fields']
            # Fusionnez les informations du client et du cordage
            complete_info = {**client_info, **client_info_cordage}
            complete_order(complete_info)
            return redirect(url_for('client_bp.order_confirmation'))
        else:
            flash('Informations de cordage introuvables pour cet email.', 'warning')
            return redirect(url_for('client_bp.client'))
    else:
        flash('Aucun utilisateur trouvé avec cet email.', 'danger')
        return redirect(url_for('client_bp.client'))

@client_bp.route('/add_client', methods=['POST'])
def add_client():

    # Récuperer l'email rentrer dans le formulaire
    email = request.form['email']
    
    # Vérifiez si l'utilisateur est déjà dans la base de données
    existing_client = airtable_clients.search('Email', email)
    
    # Si oui, alors retour à la page d'accueil
    if existing_client:
        flash("L'utilisateur existe déjà dans la base de données!", "failure")
        return redirect(url_for('index'))
    
    # Création des données pour ajouter à la base de données
    client_info = {
        'Nom': request.form['nom'],
        'Prénom' : request.form['prenom'],
        'Email': request.form['email'],
        'Ville': request.form['ville'],
        'Code Postal': request.form['codepostal'],
        'Genre': request.form['genre'],
        'Date de naissance': request.form['datedenaissance']
    }

    airtable_clients.insert(client_info)

    complete_order(client_info)
    return redirect(url_for('client_bp.order_confirmation'))

@client_bp.route('/order_confirmation')
def order_confirmation():
    return "Merci pour votre commande!"