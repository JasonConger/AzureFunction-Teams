# encoding = utf-8
import sys
import json
import requests

def get_item(access_token, url):
    headers = {}
    headers["Authorization"] = "Bearer %s" % access_token
    headers["Content-type"] = "application/json"

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        response_json = None
        response_json = json.loads(r.content)
        item = response_json
        
    except Exception as e:
        raise e

    return item