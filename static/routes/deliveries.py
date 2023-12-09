from flask import Blueprint, render_template, jsonify, request
from static.routes.config import API_KEY, BASE_ID_ORDERS, ORDERS_TABLE_2
from airtable import Airtable
from datetime import datetime

deliveries_bp = Blueprint('deliveries_bp', __name__)

airtable_cordage = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)

@deliveries_bp.route('/')
def deliveries():
    livraisons_raw = airtable_cordage.get_all(view='Livraison')
    print(livraisons_raw)
    livraisons = []
    for livraison in livraisons_raw:
        livraison_id = livraison['id']

        client = livraison['fields'].get('Nom complet', '')

        date_iso = livraison['fields'].get('Delivery Date Time', '').rstrip('Z')
        if date_iso:
            datetime_livraison = datetime.fromisoformat(date_iso)
            date_livraison = datetime_livraison.strftime('%d/%m/%Y')
            heure_livraison = datetime_livraison.strftime('%H:%M') 
        else:
            date_livraison = ''
            heure_livraison = ''

        adresse_livraison = livraison['fields'].get('Adresse de livraison', '')

        téléphone = livraison['fields'].get('Téléphone', '')

        note = livraison['fields'].get('Notes', '')

        livraisons.append({
            'id': livraison_id,
            'client': client,
            'date_livraison': date_livraison, 
            'heure_livraison': heure_livraison,
            'adresse_de_livraison': adresse_livraison,
            'téléphone': téléphone,
            'Note': note
        })

        livraisons.sort(key=lambda x: x['date_livraison'] if x['date_livraison'] else datetime.max)

    return render_template('livraisonpage.html', livraisons=livraisons)

@deliveries_bp.route('/enregistrer-note/<commandeId>', methods=['POST'])
def enregistrer_note(commandeId):
    data = request.json
    note = data.get('note', '')
    print(note)
    try:
        airtable_cordage .update(commandeId, {'Notes': note})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500