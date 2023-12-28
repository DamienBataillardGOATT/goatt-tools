from flask import Blueprint, render_template, jsonify, request
from static.scripts.airtable import get_atelier, get_decathlon, update_note, finish_commande
from datetime import datetime, timedelta

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/')
def page_de_latelier():
    commandes_raw = get_atelier()

    commandes_info = {}
    for commande in commandes_raw:
        commande_id = commande['id']

        shopify_url = commande['fields'].get('Shopify Order url', '')

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

        cordage = commande['fields'].get('Cordage', '')
        quantité = commande['fields'].get('# raquettes','')
        cordage_formatte = f"{quantité}x {cordage}" if quantité and cordage else ''

        tension = commande['fields'].get('Tension', '')

        articles_str = commande['fields'].get('Articles', '')
        articles= articles_str.split('\n')

        status_recup = commande['fields'].get('Statut récup', '')
        status_pose = commande['fields'].get('Statut pose', '')
        status_livraison = commande['fields'].get('Statut livraison', '')


        note = commande['fields'].get('Notes', '')

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

    for commande_id, commande in commandes_info.items():
        status_recup = commande.get('status_recup', '')
        status_pose = commande.get('status_pose', '')
        status_livraison = commande.get('status_livraison', '')


        if status_recup == 'To Do':
            commandes_a_recuperer.append(commande)
        elif status_recup == 'Done' and status_pose == 'To Do':
            commandes_a_poser.append(commande)
        elif status_recup == 'Done' and status_pose == 'Done' and status_livraison == 'To Do':
            commandes_a_livrer.append(commande)

    return render_template('page de atelier.html', commandes_a_recuperer=commandes_a_recuperer, commandes_a_poser=commandes_a_poser, commandes_a_livrer=commandes_a_livrer)

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
