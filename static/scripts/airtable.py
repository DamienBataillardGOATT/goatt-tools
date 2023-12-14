from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE, BASE_ID_ORDERS, ORDERS_TABLE, BASE_ID_PRODUCTS, PRODUCTS_TABLE, ORDERS_TABLE_2, BASE_ID_DECATHLON, DECATHLON_TABLE
from airtable import Airtable

airtable_strings = Airtable(BASE_ID_PRODUCTS, PRODUCTS_TABLE, API_KEY)
airtable_orders = Airtable(BASE_ID_ORDERS, ORDERS_TABLE, API_KEY)
airtable_clients = Airtable(BASE_ID_LEADS, CLIENT_TABLE, API_KEY)
airtable_cordage = Airtable(BASE_ID_ORDERS, ORDERS_TABLE_2, API_KEY)
airtable_decathlon = Airtable(BASE_ID_DECATHLON, DECATHLON_TABLE, API_KEY)

def get_all_strings():
    return airtable_strings.get_all()

def get_all_orders():
    return airtable_cordage.get_all()

def get_livraison():
    return airtable_cordage.get_all(view='Livraison')

def get_atelier():
    return airtable_cordage.get_all(view='Atelier')

def get_decathlon():
    return airtable_decathlon.get_all(view='Vue atelier')

def search_client(search_email):
    return airtable_clients.search('Email', search_email)

def search_client_in_cordage(search_email):
    return airtable_cordage.search('Email', search_email)

def create_order(data):
    return airtable_orders.insert(data)

def update_note(commandeId, data):
    return airtable_cordage.update(commandeId, data)

def finish_commande(commandeId):
    return airtable_cordage.update(commandeId, {'Statut pose': 'Done'})

def add_client(client_info):
    return airtable_clients.insert(client_info)
