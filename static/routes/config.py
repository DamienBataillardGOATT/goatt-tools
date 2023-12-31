import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID_LEADS = os.getenv('AIRTABLE_BASE_ID_LEADS')
BASE_ID_PRODUCTS = os.getenv('AIRTABLE_BASE_ID_PRODUCTS')
BASE_ID_ORDERS = os.getenv('AIRTABLE_BASE_ID_COMMANDES')
BASE_ID_DECATHLON = os.getenv('AIRTABLE_BASE_ID_DECATHLON')
CLIENT_TABLE_ID = os.getenv('AIRTABLE_ID_CLIENT')
PRODUCTS_TABLE_ID = os.getenv('AIRTABLE_ID_PRODUCTS')
ORDERS_TABLE_ID = os.getenv('AIRTABLE_ID_ORDERS')
ORDERS_TABLE_2_ID = os.getenv('AIRTABLE_ID_ORDERDS2')
DECATHLON_TABLE_ID = os.getenv('AIRTABLE_ID_DECATHLON')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_PASSWORD = os.getenv('SHOPIFY_PASSWORD')
SHOPIFY_SHOP_NAME = os.getenv('SHOPIFY_SHOP_NAME')