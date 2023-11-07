import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from airtable import Airtable
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Configuration Airtable
API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID_LEADS = os.getenv('AIRTABLE_BASE_ID_LEADS')
BASE_ID_PRODUCTS = os.getenv('AIRTABLE_BASE_ID_PRODUCTS')
BASE_ID_COMMANDES = os.getenv('AIRTABLE_BASE_ID_COMMANDES')
CLIENT_TABLE = 'leads'
PRODUCTS_TABLE = 'strings'
COMMANDES_TABLE = 'Cordage test'

airtable_clients = Airtable(BASE_ID_LEADS ,CLIENT_TABLE, API_KEY)
airtable_cordages = Airtable(BASE_ID_PRODUCTS,PRODUCTS_TABLE, API_KEY)
airtable_commandes = Airtable(BASE_ID_COMMANDES, COMMANDES_TABLE, API_KEY)

def calculate_age(birthdate):
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def complete_order(client_info):
    order_data = session.get('order_data', {})
    
    # Convertissez la date de naissance en objet datetime pour calculer l'âge
    birthdate = datetime.strptime(client_info['Date de naissance'], '%Y-%m-%d')
    age = calculate_age(birthdate)
    
    # Ajoutez les informations du client à order_data
    order_data.update({
        'Email': client_info['Email'],
        'Nom complet': f"{client_info['Prénom']} {client_info['Nom']}",
        'Date de naissance': client_info['Date de naissance'],
        'Age': age,
        'Sexe': client_info['Genre'],
    })

    print(order_data)
    
    # Insérez la commande complète dans la base de données Airtable
    airtable_commandes.insert(order_data)

    # Nettoyez la session
    session.pop('order_data', None)
    return redirect(url_for('order_confirmation'))

@app.route('/')
def commande():
    # Extraire les données de la base de données
    cordages_raw = airtable_cordages.get_all()

    # Filtrer pour ne garder que les cordages en stock
    cordages_en_stock = [cordage for cordage in cordages_raw if cordage['fields'].get('En stock')]

    # Extraire les valeurs uniques des marques et les prix pour les cordages en stock
    cordages_info = {cordage['fields'].get('String', ''): {'prix': cordage['fields'].get('price', 0)} for cordage in cordages_en_stock}

    # Trier les cordages par marque dans l'ordre alphabétique
    cordages_info_sorted = dict(sorted(cordages_info.items()))
    
    return render_template('index.html', cordages_info=cordages_info_sorted)

@app.route('/client')
def client():    
    return render_template('client.html')

@app.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']

    # Utilisez l'API Airtable pour rechercher l'utilisateur par e-mail
    client_info = airtable_clients.search('Email', search_email)
    
    if client_info:
        client_info = client_info[0]['fields']
        complete_order(client_info)
        return redirect(url_for('order_confirmation'))
    else:
        flash('Aucun utilisateur trouvé avec cet email.', 'danger')
        return redirect(url_for('client'))
    
@app.route('/add_client', methods=['POST'])
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
    return redirect(url_for('order_confirmation'))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Récupérer les données du formulaire
    option_recuperation = request.form['option_recuperation']
    option_livraison = request.form['option_livraison']
    date_livraison = request.form['date_recuperation']
    heure_recuperation = request.form['heure_recuperation']

     # Préparer les données pour la récupération
    if option_recuperation == 'adresse':
        adresse_recuperation = request.form['adresse_recuperation']
    elif option_recuperation == 'magasin':
        magasin_recuperation = request.form['magasin_recuperation']
    
    # Préparer les données pour la livraison
    if option_livraison == 'adresse':
        adresse_livraison = request.form['adresse_livraison']
    elif option_livraison == 'magasin':
        magasin_livraison = request.form['magasin_livraison']

    # Créer un dictionnaire avec les données de la commande
    order_data = {
        'Articles': f"{request.form['cordage_quantite']}x {request.form['cordage_id']}",
        'Date de récupération': request.form['date_depot'],
        'Heure de récupération': int(heure_recuperation),
        'Adresse de récupération': adresse_recuperation if option_recuperation == 'adresse' else None,
        'Adresse de livraison': adresse_livraison if option_livraison == 'adresse' else None,
    }

    # Stockez les données de la commande dans la session pour les utiliser après la création ou la récupération du client
    session['order_data'] = order_data

    # Redirection vers la page client pour vérifier si c'est une nouvelle commande ou non
    return redirect(url_for('client'))

@app.route('/order_confirmation')
def order_confirmation():
    # Afficher une page de confirmation de commande
    return "Merci pour votre commande!"

if __name__ == '__main__':
    app.run(debug=True)
