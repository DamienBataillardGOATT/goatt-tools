from flask import Blueprint, render_template, jsonify, request
from static.scripts.airtable import get_atelier, update_note, finish_commande
from datetime import datetime, timedelta

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/')
def workshop_page():
    response = get_atelier()

    # Check if the response contains 'records'
    if 'records' in response:
        commandes_raw = response['records']
    else:
        commandes_raw = []

    commandes_info = {}
    for commande in commandes_raw:
        fields = commande.get('fields', {})
        commande_id = commande['id']

        shopify_url = fields.get('Shopify Order url', '')
        client = fields.get('Nom complet', '')

        date_iso = fields.get('Delivery Date Time', '').rstrip('Z')
        if date_iso:
            datetime_livraison = datetime.fromisoformat(date_iso)
            date_livraison = datetime_livraison.strftime('%d/%m/%Y')
            heure_livraison = datetime_livraison.strftime('%H:%M') 
        else:
            date_livraison = ''
            heure_livraison = ''

        téléphone = fields.get('Téléphone', '')
        cordage = fields.get('Cordage', '')
        quantité = fields.get('# raquettes', '')
        cordage_formatte = f"{quantité}x {cordage}" if quantité and cordage else ''
        tension = fields.get('Tension', '')
        articles_str = fields.get('Articles', '')
        articles = articles_str.split('\n')
        status_recup = fields.get('Statut récup', '')
        status_pose = fields.get('Statut pose', '')
        status_livraison = fields.get('Statut livraison', '')
        note = fields.get('Notes', '')

        commandes_info[commande_id] = {
            'id': commande_id,
            'shopify_url': shopify_url,
            'client': client,
            'date_livraison': date_livraison, 
            'heure_livraison': heure_livraison,
            'cordage': cordage_formatte, 
            'telephone': téléphone,
            'quantite': quantité,
            'tension': tension,
            'status_recup': status_recup,
            'status_pose': status_pose,
            'status_livraison': status_livraison,
            'note': note,
            'articles': articles,
            'type': 'B2C'
        }

    commandes_a_recuperer = []
    commandes_a_poser = []
    commandes_a_livrer = []

    for commande in commandes_info.values():
        if commande['status_recup'] == 'To Do':
            commandes_a_recuperer.append(commande)
        elif commande['status_recup'] == 'Done' and commande['status_pose'] == 'To Do':
            commandes_a_poser.append(commande)
        elif commande['status_recup'] == 'Done' and commande['status_pose'] == 'Done' and commande['status_livraison'] == 'To Do':
            commandes_a_livrer.append(commande)

    return render_template('workshop_page.html', commandes_a_recuperer=commandes_a_recuperer, commandes_a_poser=commandes_a_poser, commandes_a_livrer=commandes_a_livrer)

@orders_bp.route('/writeNote/<commandeId>', methods=['POST'])
def writeNote(commandeId):
    data = request.json
    note = data.get('note', '')

    try:
        update_note(commandeId, note)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@orders_bp.route('/finishCommande/<commandeId>', methods=['POST'])
def finishCommande(commandeId):
    try:
        finish_commande(commandeId)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
