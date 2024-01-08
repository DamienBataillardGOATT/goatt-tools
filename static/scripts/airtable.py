from static.routes.config import API_KEY, BASE_ID_LEADS, CLIENT_TABLE_ID, BASE_ID_ORDERS, PRODUCTS_TABLE_ID, BASE_ID_PRODUCTS, ORDERS_TABLE_2_ID, ORDERS_TABLE_ID, DECATHLON_TABLE_ID, BASE_ID_DECATHLON
import requests

def get_all_strings():
    url = f'https://api.airtable.com/v0/{BASE_ID_PRODUCTS}/{PRODUCTS_TABLE_ID}'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}

def get_all_orders():
    url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}?view=Global'
    headers = {'Authorization': f'Bearer {API_KEY}'}

    all_orders = []
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            all_orders.extend(data.get('records', []))

            # Check if there's more data to fetch
            offset = data.get('offset')
            if offset:
                url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}?view=Global&offset={offset}'
            else:
                break
        else:
            return {'error': response.json()}

    return {'records': all_orders}

def get_atelier():
    url = (f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}'
           f'?view=Global&sort[0][field]=Created%20time&sort[0][direction]=desc')
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
    
def get_decathlon():
    url = f'https://api.airtable.com/v0/{BASE_ID_DECATHLON}/{DECATHLON_TABLE_ID}?view=Vue atelier'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}

def search_client(search_email):
    url = f'https://api.airtable.com/v0/{BASE_ID_LEADS}/{CLIENT_TABLE_ID}?filterByFormula=SEARCH("{search_email}", {{Email}})'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['records']:
            client_record = data['records'][0]
            client_info = {
                'Nom': client_record['fields'].get('Nom', ''),
                'Prénom': client_record['fields'].get('Prénom', ''),
                'Email': client_record['fields'].get('Email', ''),
                'Téléphone': client_record['fields'].get('Téléphone', '')
            }
            return client_info
        else:
            return None
    else:
        return {'error': response.json()}

def search_client_in_cordage(search_email):
    url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}?filterByFormula=SEARCH("{search_email}", {{Email}})'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
    
def create_order(data):
    formatted_data = {"fields": data}
    url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_ID}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=formatted_data)
    print(response)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
    
def update_note(commandeId, note):
    url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}/{commandeId}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {"fields": {"Notes": note}}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
    
def finish_commande(commandeId):
    url = f'https://api.airtable.com/v0/{BASE_ID_ORDERS}/{ORDERS_TABLE_2_ID}/{commandeId}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {"fields": {"Statut pose": "Done"}}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
    
def add_client_to_airtable(client_info):
    formatted_client_info = {"fields": client_info}
    url = f'https://api.airtable.com/v0/{BASE_ID_LEADS}/{CLIENT_TABLE_ID}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=formatted_client_info)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': response.json()}
