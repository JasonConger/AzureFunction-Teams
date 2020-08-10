import logging
import os
import requests
import json
import azure.functions as func
from ..utils import auth as azauth
from ..utils import utils as azutils

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('callRecord function processed a request.')

    '''
    If there is a validationToken parameter in the query string, 
    then this is the request that Office 365 sends to check that this is a valid endpoint.
    Just send the validationToken back.
    '''
    if 'validationToken' in req.params:
        return func.HttpResponse(req.params.get('validationToken'))
    
    payload = req.get_json()
    # If this is a call record, write it to Splunk HEC
    if (("value" in payload) and ("resourceData" in payload["value"][0]) and ("id" in payload["value"][0]["resourceData"])):
        client_id = os.environ["CLIENT_ID"]
        client_secret = os.environ["CLIENT_SECRET"]
        tenant_id = os.environ["TENANT_ID"]
        splunk_hec_url = os.environ["SPLUNK_HEC_URL"]
        splunk_hec_token = os.environ["SPLUNK_HEC_TOKEN"]

        if splunk_hec_url.endswith("/"):
            splunk_hec_url = "%sservices/collector" % splunk_hec_url
        else:
            splunk_hec_url = "%s/services/collector" % splunk_hec_url

        # Try to get an access token
        access_token = azauth.get_graph_access_token(client_id, client_secret, tenant_id)

        if(access_token):
            try:
                # Get call record and send it to Splunk HEC
                url = "https://graph.microsoft.com/beta/communications/callRecords/%s?$expand=sessions($expand=segments)" % payload["value"][0]["resourceData"]["id"]
                call_record = azutils.get_item(access_token, url)

                # Write to HEC here
                headers = {}
                headers["Authorization"] = "Splunk %s" % splunk_hec_token
                headers["Content-type"] = "application/json"

                event = {}
                event["event"] = json.dumps(call_record)

                r = requests.post(splunk_hec_url, data=json.dumps(event), headers=headers)
                r.raise_for_status()

                # Send a 202 (accepted) if the event was sucessfully written to HEC
                return func.HttpResponse(status_code=202)

            except Exception as e:
                raise e
