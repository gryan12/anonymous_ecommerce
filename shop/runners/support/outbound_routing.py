import requests
import logging
import json

###credentials
AGENT_URL = ""

def set_agent_url(url):
    global AGENT_URL
    AGENT_URL = url

def post(url, data=None):
    if data:
        response = requests.post(url, json=data)
    else:
        response = requests.post(url)

    if response.status_code == 200:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(e)
            raise
    elif response.status_code == 422:
        print(response.json())
    else:
        logging.debug(str(response.status_code) + response.reason)
        return None

def get(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(e)
            raise
    else:
        logging.debug(str(response.status_code) + response.reason)
        return None

##credentials
def send_cred_offer(offer_request):
    req_url = AGENT_URL + "/issue-credential/send-offer"
    return post(req_url, data=offer_request)

def send_cred_request(id):
    req_url = AGENT_URL + f"/issue-credential/records/{id}/send-request"
    return post(req_url)

def issue_credential(ex_id, credential):
    req_url = AGENT_URL + f"/issue-credential/records/{ex_id}/issue"
    return post(req_url, credential)

def get_credential(cred_id):
    req_url = AGENT_URL + f"/credential/{cred_id}"
    return get(req_url)

def get_credentials():
    req_url = AGENT_URL + "/credential"
    return get(req_url)

def get_credentials(id):
    req_url = AGENT_URL + f"/present-proof/records/{id}/credentials"
    return get(req_url)

def remove_credential(id):
    req_url = AGENT_URL + f"/credential/{id}/remove"
    return post(req_url)

def get_cred_ex_record(credex_id):
    req_url = AGENT_URL + f"/issue-credential/records/{credex_id}"
    return get(req_url)

def get_cred_ex_records():
    req_url = AGENT_URL + f"/issue-credential/records"
    return get(req_url)

##proofs
def send_proof_request(proof_req):
    req_url = AGENT_URL + "/present-proof/send-request"
    return post(req_url, data=proof_req)

def present_proof(presentation, id):
    req_url = AGENT_URL + f"present-proof/records/{id}/verify-presentation"
    return post(req_url, data=presentation)

def send_presentation(presentation, id):
    req_url = AGENT_URL + f"/present-proof/records/{id}/send-presentation"
    return post(req_url, data=presentation)

def verify_presentation(id):
    req_url = AGENT_URL + f"/present-proof/records/{id}/verify-presentation"
    return post(req_url)

def get_pres_ex_details(presex_id):
    req_url = AGENT_URL + f"/present-proof/records/{presex_id}"
    return get(req_url)

def get_pres_ex_records():
    req_url = AGENT_URL + "/present-proof/records"
    return get(req_url)

##connections
def create_invite():
    req_url = AGENT_URL + "/connections/create-invitation"
    return post(req_url)

def get_connections(conn_id = None):
    query_url = AGENT_URL + "/connections"
    if conn_id:
        query_url = query_url + f"/{conn_id}"
    return get(query_url)

def receive_invite(invite_json):
    req_url = AGENT_URL + "/connections/receive-invitation"
    return post(req_url, data=invite_json)

def send_message(content, id):
    req_url = AGENT_URL + f"/connections/{id}/send-message"
    return post(req_url, data=content)

##schemas

def register_schema(schema):
    req_url = AGENT_URL + "/schemas"
    return post(req_url, data=schema)

def register_creddef(creddef):
    req_url = AGENT_URL + "/credential-definitions"
    return post(req_url, creddef)


def get_public_did():
    req_url = AGENT_URL + "/wallet/did/public"
    return get(req_url)

##misc

def get_status():
    req_url = AGENT_URL + "/status"
    return get(req_url)

def get_public_did():
    req_url = AGENT_URL + "/wallet/did/public"
    return get(req_url)
