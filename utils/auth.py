# encoding = utf-8
import requests
import json

def get_graph_access_token(client_id, client_secret, tenant_id):
    endpoint = "https://login.microsoftonline.com/%s/oauth2/v2.0/token" % tenant_id
    payload = {
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    try:
        response = requests.post(endpoint, data=payload).json()
        if 'access_token' in response:
            return response['access_token']
        else:
            raise Exception("Could not get access token.")
    except Exception as e:
        raise e