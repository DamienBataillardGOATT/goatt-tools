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
def reparation():

    # Extraire les données de la base de données
    cordages_raw = airtable_cordages.get_all()

    # Extraire les valeurs uniques
    unique_marques = set(cordage['fields'].get('String', '') for cordage in cordages_raw)
    
    return render_template('index.html', marques=sorted(unique_marques), cordages = cordages_raw)

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
