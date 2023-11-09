import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID_LEADS = os.getenv('AIRTABLE_BASE_ID_LEADS')
BASE_ID_PRODUCTS = os.getenv('AIRTABLE_BASE_ID_PRODUCTS')
BASE_ID_COMMANDES = os.getenv('AIRTABLE_BASE_ID_COMMANDES')
CLIENT_TABLE = 'leads'
PRODUCTS_TABLE = 'strings'
COMMANDES_TEST_TABLE = 'Cordage test'
COMMANDES_TABLE = 'Cordage'