import requests
from dotenv import load_dotenv
import os
import getopt
import sys
import json
import re
from msal import ConfidentialClientApplication

# Load environment variables from .env file
load_dotenv()
# Retrieve environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')
SCOPE = ["https://labassist.pnnl.gov/proxy/.default"]


# URL to request a token from Azure AD
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/"

# Request token from Azure AD using Client Credentials flow
def get_access_token():
    app = ConfidentialClientApplication(client_id=CLIENT_ID, client_credential=CLIENT_SECRET, authority=TOKEN_URL)  
    response = app.acquire_token_for_client(scopes=SCOPE)
    if 'error' in response:
        raise Exception(f"Error acquiring token: {response['error_description']}")
    return response['access_token']

# Make a request to the OAuth Proxy endpoint
def call_elastic_search():
    access_token = get_access_token()
    url = "https://labassist.pnnl.gov/proxy/actman/elasticsearch/hub-suggestions-people/_search?q=skills:Nuclear+Reactors"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    return response

if __name__ == "__main__":
    response = call_elastic_search()