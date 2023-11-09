from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_COMMANDES, COMMANDES_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, COMMANDES_TEST_TABLE
from airtable import Airtable

# Création d'un Blueprint pour les routes client
order_bp = Blueprint('order_bp', __name__)

# Initialisation de la connexion Airtable pour les clients
airtable_cordages = Airtable(BASE_ID_PRODUCTS,PRODUCTS_TABLE, API_KEY)

@order_bp.route('/')
def order():
    # Extraire les données de la base de données
    cordages_raw = airtable_cordages.get_all()

    # Filtrer pour ne garder que les cordages en stock
    cordages_en_stock = [cordage for cordage in cordages_raw if cordage['fields'].get('En stock')]

    # Extraire les valeurs uniques des marques et les prix pour les cordages en stock
    cordages_info = {cordage['fields'].get('String', ''): {'prix': cordage['fields'].get('price', 0)} for cordage in cordages_en_stock}

    # Trier les cordages par marque dans l'ordre alphabétique
    cordages_info_sorted = dict(sorted(cordages_info.items()))
    
    return render_template('index.html', cordages_info=cordages_info_sorted)

@order_bp.route('/submit_order', methods=['POST'])
def submit_order():

    # Récupérer les données du formulaire
    option_recuperation = request.form['option_recuperation']
    option_livraison = request.form['option_livraison']
    heure_recuperation = request.form['heure_recuperation']
    date_livraison = request.form['date_recuperation']
    heure_livraison = request.form['creneauSelectionne']
    prix_total_panier = request.form['prixTotalPanier']
    
    # Initialiser les variables pour les adresses
    adresse_recuperation = None
    adresse_livraison = None
    adresse_magasin_recuperation = None
    adresse_magasin_livraison = None

    # Préparer les données pour la récupération
    if option_recuperation == 'adresse':
        adresse_recuperation = request.form['adresse_recuperation']
    elif option_recuperation == 'magasin':
        adresse_magasin_recuperation = request.form['adresse_magasin']  # Récupérer l'adresse du magasin de récupération
    
    # Préparer les données pour la livraison
    if option_livraison == 'adresse':
        adresse_livraison = request.form['adresse_livraison']
    elif option_livraison == 'magasin':
        adresse_magasin_livraison = request.form['adresse_magasin']  # Récupérer l'adresse du magasin de livraison

    # Créer un dictionnaire avec les données de la commande
    order_data = {
        'Articles': f"{request.form['cordage_quantite']}x {request.form['cordage_id']}",
        'Quantité': request.form['cordage_quantite'],
        'Date de récupération': request.form['date_depot'],
        'Heure de récupération': int(heure_recuperation),
        'Adresse de récupération': adresse_recuperation if option_recuperation == 'adresse' else adresse_magasin_recuperation,
        'Date de livraison': date_livraison,
        'Heure de livraison': int(heure_livraison),
        'Adresse de livraison': adresse_livraison if option_livraison == 'adresse' else adresse_magasin_livraison,
        'Prix': float(prix_total_panier),
    }

    # Stockez les données de la commande dans la session pour les utiliser après la création ou la récupération du client
    session['order_data'] = order_data

    # Redirection vers la page client pour vérifier si c'est une nouvelle commande ou non
    return redirect(url_for('client_bp.client'))