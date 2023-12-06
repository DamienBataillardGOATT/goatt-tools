from flask import Flask, render_template
from static.routes.order_routes import order_bp
from static.routes.client_routes import client_bp
from static.routes.order_page import orderpage_bp
from static.routes.livraisonpage import livraison_bp
import os

# Create a Flask application instance
app = Flask(__name__)

# Configure the secret key for session data
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Register the Blueprints with their URL prefixes
app.register_blueprint(client_bp, url_prefix='/client')
app.register_blueprint(order_bp, url_prefix='/order')
app.register_blueprint(orderpage_bp, url_prefix='/orderpage')
app.register_blueprint(livraison_bp, url_prefix='/livraisonpage')

# Define the root route of the application
@app.route('/')
def index():
    return render_template('index.html')

# Run the application if this script is executed as the main program
if __name__ == '__main__':
    app.run(debug=True)
