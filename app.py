from flask import Flask, redirect, url_for
from static.routes.order_routes import order_bp
from static.routes.client_routes import client_bp
import os
# Importez d'autres Blueprints ici si nécessaire

app = Flask(__name__)

# Configuration de la clé secrète pour les sessions
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Enregistrement des Blueprints
app.register_blueprint(client_bp, url_prefix='/client')
app.register_blueprint(order_bp, url_prefix='/order')


@app.route('/')
def index():
    return redirect(url_for('order_bp.order')) 

# Autres routes globales de l'application peuvent être ajoutées ici

if __name__ == '__main__':
    app.run(debug=True)
