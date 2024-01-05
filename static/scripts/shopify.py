from static.routes.config import SHOPIFY_API_KEY
import requests

def get_shopify_headers():
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_API_KEY,
    }

def create_shopify_customer(email, first_name, last_name):
    url = f"https://goatt-tennis.myshopify.com/admin/api/2021-01/customers.json"
    data = {
        "customer": {
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }
    }
    response = requests.post(url, json=data, headers=get_shopify_headers())
    return response.json().get('customer')

def search_shopify_customer(email, first_name, last_name):
    url = f"https://goatt-prod.myshopify.com/admin/api/2023-04/customers/search.json?query=email:{email}"
    response = requests.get(url, headers=get_shopify_headers())
    if response.status_code == 200:
        customers = response.json().get('customers', [])
        if customers:
            customer_id = customers[0].get('id') 
            return customer_id
        else:
            print("Aucun client trouvé.")
            new_customer = create_shopify_customer(email, first_name, last_name)
            return new_customer.get('id') if new_customer else None
    else:
        raise Exception(f"Failed to search customer: {response.text}")

def create_draft_order(data):
    url = f"https://goatt-shopify.onrender.com/create_draft_order_v2"

    lineItems = [{
        "variant_id": data['variant_id'],
        "requires_shipping": 'false',
        "quantity": data['quantité']
    },
     {
        "variant_id": '42066577457335',
        "requires_shipping": 'false',
        "quantity": data['quantité']
    },]

    draft_order_data = {
        "draft_order": {
            "line_items": lineItems,
            "customer": {
                "id": data['shopify_customer_id']
            },
            "shipping_address": {
                "address1": data['pickup_address'],
                "phone": data['phone'],
                "last_name": data['nom'],
                "first_name": data['prenom'],
                "city": data['pickup_town'],
                "country": "France",
                "zip": data['pickup_postal_code']
            },
            "shipping_line": {
                "custom": True,
                "price": data['price_delivery'],
                "title": 'Récupération et Livraison - ' + data['pose_type']
            },
        }
    }
    
    response = requests.post(url, json=draft_order_data, headers=get_shopify_headers())
    if response.status_code == 200:
        response_data = response.json()
        invoice_url = response_data['draft_order']['admin_graphql_api_id']
        order_id = invoice_url.split('/')[-1]
        order_url = f"https://admin.shopify.com/store/goatt-prod/draft_orders/{order_id}"
        return order_id, order_url
    else:
        return None 
    
