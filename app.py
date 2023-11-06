from flask import Flask, render_template, request, redirect, url_for, flash
from airtable import Airtable

app = Flask(__name__)
app.secret_key = '1254'

# Configuration Airtable
API_KEY = 'pat8ocpNqxyGQpATw.ee85cef19f90dcd5a070e8057b7e8d84d148b116471ce54843d8c4f5f3ae1465'
BASE_ID = 'app35hW4vdSCSF1zJ'
CLIENT_TABLE = 'Leads'

airtable_clients = Airtable(BASE_ID,CLIENT_TABLE, API_KEY)

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/search_client', methods=['POST'])
def search_client():
    search_email = request.form['search_email']
    
    # Utilisez l'API Airtable pour rechercher l'utilisateur par e-mail
    client_record = airtable_clients.search('Email', search_email)
    
    if client_record:
        # L'utilisateur a été trouvé, affichez ses informations
        # (Assurez-vous que les champs correspondent à ceux de votre table Airtable)
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
