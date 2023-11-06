from flask import Flask, render_template, request, redirect, url_for, flash
from airtable import Airtable

app = Flask(__name__)
app.secret_key = '1254'

# Configuration Airtable
API_KEY = 'keyS4y9yGGRj96S7V'
BASE_ID = 'patkrzVdzKq4ayajx.7d18d25b2b81051d5b1ae99788e8a49747daa7f6068bb40b9c8fdeac7ca77dc9'
CLIENT_TABLE = 'Leads'

airtable_clients = Airtable(BASE_ID,CLIENT_TABLE, API_KEY)

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/reparation')
def reparation():

    # Extraire les données de la base de données
    cordages_raw = airtable_cordages.get_all()
    
    # Extraire les valeurs uniques
    unique_marques = set(cordage['fields'].get('Marque', '') for cordage in cordages_raw)
    unique_modeles = set(cordage['fields'].get('Modèle', '') for cordage in cordages_raw)
    unique_tailles = set(cordage['fields'].get('Size', '') for cordage in cordages_raw)
    
    return render_template('reparation.html', marques=sorted(unique_marques), modeles=sorted(unique_modeles), tailles=sorted(unique_tailles), cordages = cordages_raw)

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
        'Code postal': request.form['codepostal'],
        'Genre': request.form['genre'],
        'Date de naissance': request.form['datedenaissance']
    }

    # Ajout à la base de données
    airtable_clients.insert(data)

    # Message de validation
    flash("L'utilisateur a ete ajouter à la base de données!", "success")

    # Retour à la page d'accueil
    return redirect(url_for('index'))

@app.route('/choose_cordage', methods=['POST'])
def choose_cordage():

    # Récuperer l'email rentrer dans le formulaire
    email = request.form['email']
    
    # Vérifiez si l'utilisateur est déjà dans la base de données
    existing_client = airtable_clients.search('Email', email)
    
    # Si non, rédirection vers la page d'accueil pour s'inscrire
    if not existing_client:
        flash("L'utilisateur n'existe pas dans la base de données. Veuillez vous inscrire d'abord.", "failure")
        return redirect(url_for('index'))
    
    # Si l'utilisateur est dans la base de données, ajoutez sa réservation
    data = {
        'Email': email,
        'Marque': request.form['cordage_id'],
        'Modèle': request.form['modele_id'],  # Assurez-vous que le nom du champ correspond à celui de votre formulaire
        'Size': request.form['taille_id'],  # Assurez-vous que le nom du champ correspond à celui de votre formulaire
        'Date de récupération': request.form['date_recuperation']
    }
    
    # Insérez les données dans la table "reservation"
    airtable_reservation.insert(data)
    
    # Message de confirmation
    flash("Votre réservation a été effectuée avec succès!", "success")

    #Retour à la page reparation
    return redirect(url_for('reparation'))

if __name__ == '__main__':
    app.run(debug=True)
