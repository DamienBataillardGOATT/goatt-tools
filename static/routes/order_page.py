from flask import Blueprint, render_template, jsonify
from static.routes.config import API_KEY, BASE_ID_ORDERS, ORDERS_TABLE_2
from airtable import Airtable
from datetime import datetime

orderpage_bp = Blueprint('orderpage_bp', __name__)

airtable_cordarge = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)

@orderpage_bp.route('/')
def orderpage():
    commandes_raw = airtable_cordarge.get_all(view='Atelier')

    commandes_info = {}
    for commande in commandes_raw:
        commande_id = commande['id']

        client = commande['fields'].get('Nom complet', '')
        
        date_iso = commande['fields'].get('Delivery Date Time', '').rstrip('Z')
        date_livraison = datetime.fromisoformat(date_iso).strftime('%d/%m/%Y') if date_iso else ''

        cordage = commande['fields'].get('Cordage', '')
        quantité = commande['fields'].get('# raquettes','')
        cordage_formatte = f"{quantité}x {cordage}" if quantité and cordage else ''

        tension = commande['fields'].get('Tension', '')

        commandes_info[client] = {
            'id': commande_id,
            'date_livraison': date_livraison, 
            'Cordage': cordage_formatte, 
            'Tension': tension
        }

    return render_template('orderpage.html', commandes_info=commandes_info)

@orderpage_bp.route('/terminer-commande/<commandeId>', methods=['POST'])
def terminer_commande(commandeId):
    try:
        airtable_cordarge.update(commandeId, {'Statut pose': 'Done'})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
