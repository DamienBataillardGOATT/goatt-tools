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
BASE_ID_COMMANDES = os.getenv('AIRTABLE_BASE_ID_COMMANDES')
CLIENT_TABLE = 'leads'
PRODUCTS_TABLE = 'strings'
COMMANDES_TABLE = 'Cordage'

airtable_clients = Airtable(BASE_ID_LEADS ,CLIENT_TABLE, API_KEY)
airtable_cordages = Airtable(BASE_ID_PRODUCTS,PRODUCTS_TABLE, API_KEY)
airtable_commandes = Airtable(BASE_ID_COMMANDES, COMMANDES_TABLE, API_KEY)


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

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Récupérer les données du formulaire
    cordage_id = request.form['cordage_id']
    quantite = request.form['cordage_quantite']
    option_recuperation = request.form['option_recuperation']
    option_livraison = request.form['option_livraison']

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
        'CordageID': cordage_id,
        'Quantite': quantite,
        'OptionRecuperation': option_recuperation,
        'AdresseRecuperation': adresse_recuperation if option_recuperation == 'adresse' else None,
        'MagasinRecuperation': magasin_recuperation if option_recuperation == 'magasin' else None,
        'OptionLivraison': option_livraison,
        'AdresseLivraison': adresse_livraison if option_livraison == 'adresse' else None,
        'MagasinLivraison': magasin_livraison if option_livraison == 'magasin' else None,
    }

    print(order_data)
    # Ajout à la base de données
    """try:
        airtable_commandes.insert(data)
        flash("La commande a été ajoutée avec succès à la base de données!", "success")
    except Exception as e:
        flash("Une erreur est survenue lors de l'ajout de la commande à la base de données.", "error")
        return redirect(url_for('index'))"""

    # Redirection vers la page de confirmation
    return redirect(url_for('order_confirmation'))

@app.route('/order_confirmation')
def order_confirmation():
    # Afficher une page de confirmation de commande
    return "Merci pour votre commande!"


if __name__ == '__main__':
    app.run(debug=True)
