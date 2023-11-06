from flask import Flask, render_template, request, redirect, url_for, flash
from airtable import Airtable
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Configuration Airtable
API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID_LEADS = os.getenv('AIRTABLE_BASE_ID_LEADS')
BASE_ID_PRODUCTS = os.getenv('AIRTABLE_BASE_ID_PRODUCTS')
CLIENT_TABLE = 'leads'
PRODUCTS_TABLE = 'strings'

airtable_clients = Airtable(BASE_ID_LEADS ,CLIENT_TABLE, API_KEY)
airtable_cordages = Airtable(BASE_ID_PRODUCTS,PRODUCTS_TABLE, API_KEY)


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
def index():    
    return render_template('client.html')

@app.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']

    # Utilisez l'API Airtable pour rechercher l'utilisateur par e-mail
    client_record = airtable_clients.search('Email', search_email)
    
    if client_record:
        # L'utilisateur a été trouvé, affichez ses informations
        client_info = client_record[0]['fields']
        return render_template('client_info.html', client_info=client_info)
    else:
        # L'utilisateur n'a pas été trouvé, affichez un message d'erreur
        flash('Aucun utilisateur trouvé avec cet email.', 'danger')
        return redirect(url_for('index'))
    
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
    data = {
        'Nom': request.form['nom'],
        'Prénom' : request.form['prenom'],
        'Email': request.form['email'],
        'Ville': request.form['ville'],
        'Code Postal': request.form['codepostal'],
        'Genre': request.form['genre'],
        'Date de naissance': request.form['datedenaissance']
    }

    # Ajout à la base de données
    airtable_clients.insert(data)

    # Message de validation
    flash("L'utilisateur a ete ajouter à la base de données!", "success")

    # Retour à la page d'accueil
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
