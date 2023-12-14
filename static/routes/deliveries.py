from flask import Blueprint, render_template, jsonify, request
from static.scripts.airtable import get_livraison, update_note
from datetime import datetime, timedelta

deliveries_bp = Blueprint('deliveries_bp', __name__)

@deliveries_bp.route('/')
def page_des_livraisons():

    livraisons_raw = get_livraison()

    livraisons_aujourd_hui = []
    livraisons_demain = []
    livraisons_a_venir = []

    aujourd_hui = datetime.today().date()
    demain = aujourd_hui + timedelta(days=1)

    for livraison in livraisons_raw:
        livraison_id = livraison['id']

        client = livraison['fields'].get('Nom complet', '')

        date_iso = livraison['fields'].get('Delivery Date Time', '').rstrip('Z')
        if date_iso:
            datetime_livraison = datetime.fromisoformat(date_iso)
            date_livraison = datetime_livraison.date()
            heure_livraison = datetime_livraison.time()  
        else:
            date_livraison = None
            heure_livraison = None

        adresse_livraison = livraison['fields'].get('Adresse de livraison', '')

        téléphone = livraison['fields'].get('Téléphone', '')

        livra = livraison['fields'].get('Statut livraison', '')

        articles_str = livraison['fields'].get('Articles', '')
        articles= articles_str.split('\n')

        note = livraison['fields'].get('Notes', '')

        if date_livraison == aujourd_hui:
            livraisons_aujourd_hui.append({
                'id': livraison_id,
                'client': client,
                'date_livraison': date_livraison, 
                'heure_livraison': heure_livraison,
                'adresse_de_livraison': adresse_livraison,
                'téléphone': téléphone,
                'status_livraison': livra,
                'Articles': articles,
                'Note': note
            })
        elif date_livraison == demain:
            livraisons_demain.append({
                'id': livraison_id,
                'client': client,
                'date_livraison': date_livraison, 
                'heure_livraison': heure_livraison,
                'adresse_de_livraison': adresse_livraison,
                'téléphone': téléphone,
                'status_livraison': livra,
                'Articles': articles,
                'Note': note
            })
        elif date_livraison and date_livraison > demain:
            livraisons_a_venir.append({
                'id': livraison_id,
                'client': client,
                'date_livraison': date_livraison, 
                'heure_livraison': heure_livraison,
                'adresse_de_livraison': adresse_livraison,
                'téléphone': téléphone,
                'status_livraison': livra,
                'Articles': articles,
                'Note': note
            })

    return render_template('page des livraisons.html', livraisons_aujourd_hui=livraisons_aujourd_hui, livraisons_demain=livraisons_demain, livraisons_a_venir=livraisons_a_venir)

@deliveries_bp.route('/writeNote/<commandeId>', methods=['POST'])
def writeNote(commandeId):
    data = request.json
    note = data.get('note', '')
    print(note)
    try:
        update_note(commandeId, note)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500