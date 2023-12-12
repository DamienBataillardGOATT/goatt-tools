from flask import Blueprint, render_template, jsonify, request
from static.routes.config import API_KEY, BASE_ID_ORDERS, ORDERS_TABLE_2, BASE_ID_DECATHLON, DECATHLON_TABLE
from airtable import Airtable
from datetime import datetime, timedelta

orders_bp = Blueprint('orders_bp', __name__)

airtable_cordarge = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)
airtable_decathlon = Airtable(BASE_ID_DECATHLON, DECATHLON_TABLE, API_KEY)

@orders_bp.route('/')
def page_de_latelier():
    commandes_raw = airtable_cordarge.get_all(view='Atelier')
    commandes_decathlon_raw = airtable_decathlon.get_all(view='Vue atelier')

    commandes_info = {}
    for commande in commandes_raw:
        commande_id = commande['id']

        client = commande['fields'].get('Nom complet', '')
        
        date_iso = commande['fields'].get('Delivery Date Time', '').rstrip('Z')
        if date_iso:
            datetime_livraison = datetime.fromisoformat(date_iso)
            date_livraison = datetime_livraison.strftime('%d/%m/%Y')
            heure_livraison = datetime_livraison.strftime('%H:%M') 
        else:
            date_livraison = ''
            heure_livraison = ''

        téléphone = commande['fields'].get('Téléphone', '')

        quantité = commande['fields'].get('# raquettes','')

        tension = commande['fields'].get('Tension', '')

        articles_str = commande['fields'].get('Articles', '')
        articles= articles_str.split('\n')

        note = commande['fields'].get('Notes', '')

        commandes_info[commande_id] = {
            'id': commande_id,
            'client': client,
            'date_livraison': date_livraison, 
            'heure_livraison': heure_livraison,
            'téléphone': téléphone,
            'quantité': quantité,
            'Tension': tension,
            'Note': note,
            'Articles': articles,
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

    commandes_aujourd_hui = []
    commandes_demain = []
    commandes_a_venir = []

    aujourd_hui = datetime.today().date()
    demain = aujourd_hui + timedelta(days=1)

    for commande in toutes_commandes:
        date_livraison = datetime.strptime(commande['date_livraison'], '%d/%m/%Y').date() if commande['date_livraison'] else None

        if date_livraison == aujourd_hui:
            commandes_aujourd_hui.append(commande)
        elif date_livraison == demain:
            commandes_demain.append(commande)
        elif date_livraison and date_livraison > demain:
            commandes_a_venir.append(commande)

    return render_template('page de l’atelier.html', commandes_aujourd_hui=commandes_aujourd_hui, commandes_demain=commandes_demain, commandes_a_venir=commandes_a_venir)

@orders_bp.route('/writeNote/<commandeId>', methods=['POST'])
def writeNote(commandeId):
    data = request.json
    note = data.get('note', '')

    try:
        airtable_cordarge.update(commandeId, {'Notes': note})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@orders_bp.route('/finishCommande/<commandeId>', methods=['POST'])
def finishCommande(commandeId):
    try:
        airtable_cordarge.update(commandeId, {'Statut pose': 'Done'})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
