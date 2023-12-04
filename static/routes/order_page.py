from flask import Blueprint, render_template, jsonify, request
from static.routes.config import API_KEY, BASE_ID_ORDERS, ORDERS_TABLE_2, BASE_ID_DECATHLON, DECATHLON_TABLE
from airtable import Airtable
from datetime import datetime

orderpage_bp = Blueprint('orderpage_bp', __name__)

airtable_cordarge = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)
airtable_decathlon = Airtable(BASE_ID_DECATHLON, DECATHLON_TABLE, API_KEY)

@orderpage_bp.route('/')
def orderpage():
    commandes_raw = airtable_cordarge.get_all(view='Atelier')
    commandes_decathlon_raw = airtable_decathlon.get_all(view='Vue atelier')

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

        note = commande['fields'].get('Notes', '')

        commandes_info[commande_id] = {
            'id': commande_id,
            'client': client,
            'date_livraison': date_livraison, 
            'Cordage': cordage_formatte, 
            'Tension': tension,
            'Note': note,
            'type': 'B2C'
        }

    decathlon_commandes_info = {}
    for commande in commandes_decathlon_raw:
        commande_id = commande['id']

        id_client = commande['fields'].get('id', '')

        date_brute = commande['fields'].get('decat_date', '')
        date_livraison = datetime.strptime(date_brute, '%Y-%m-%d') if date_brute else None

        cordage = commande['fields'].get('cordage', '')
        quantité = commande['fields'].get('quantité','')
        cordage_formatte = f"{quantité}x {cordage}" if quantité and cordage else ''

        tension = commande['fields'].get('tension', '')

        note = commande['fields'].get('notes_goatt', '')

        decathlon_commandes_info[commande_id] = {
            'id': commande_id,
            'client': id_client,
            'date_livraison': date_livraison, 
            'Cordage': cordage_formatte, 
            'Tension': tension,
            'Note': note,
            'type': 'B2B'
        }

    toutes_commandes = list(commandes_info.values()) + list(decathlon_commandes_info.values())

    for commande in toutes_commandes:
        try:
            commande['date_livraison'] = datetime.strptime(commande['date_livraison'], '%d/%m/%Y')
        except ValueError:
            commande['date_livraison'] = None

    toutes_commandes.sort(key=lambda x: x['date_livraison'] if x['date_livraison'] else datetime.max)

    return render_template('orderpage.html', toutes_commandes=toutes_commandes)

@orderpage_bp.route('/enregistrer-note/<commandeId>', methods=['POST'])
def enregistrer_note(commandeId):
    data = request.json
    note = data.get('note', '')
    print(note)
    try:
        airtable_cordarge.update(commandeId, {'Notes': note})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@orderpage_bp.route('/terminer-commande/<commandeId>', methods=['POST'])
def terminer_commande(commandeId):
    try:
        airtable_cordarge.update(commandeId, {'Statut pose': 'Done'})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
