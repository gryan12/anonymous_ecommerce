import json
import logging
import requests
import random
from threading import Thread
import os
import sys
import time
from flask import Flask, request, make_response, render_template

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
from runners.support.creds import build_cred, build_proof_request, build_schema
from runners.agent_proc import start_aries

##globals
LEDGER_URL = "http://172.17.0.1:9000"

##mock replacement for a db (just grping state data)
class Data:
    def __init__(self):
        self.current_connection =None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.connections = []
        self.active = False
        self.stage = 0
        self.agent_role = None

        self.bank_did = None
        self.shipper_did = None
        self.vendor_did = None

        self.presex_roles = {} #dict (placeholder cache) of <pres_ex_id> : <role>
        self.credex = {} #dict (placeholder cache) of <cred_ex_id> : <role>

    def add_connection(self, conn_id):
        self.connections.append(conn_id)
        self.current_connection = conn_id,

    def add_preview(self, creddef_id, preview):
        self.previews[creddef_id] = preview

    def add_attrs(self, creddef_id, attrs):
        self.attrs[creddef_id] = attrs


##ugly but placeholder for db
agent_data = Data()

path = os.path.join(os.getcwd(), "shop/runners/static")
print("PATH IS:",  path)

app = Flask(__name__, static_folder=path)
print("INSTANCE PATH IS:",  app.instance_path)

#### START interface routes
@app.route("/home/", methods=["GET"])
def render_interface():
    name = os.getenv("ROLE")
    return render_template("interface.html", name=name)


@app.route("/home/connections", methods=["GET"])
def render_connections():
    name = os.getenv("ROLE")
    return render_template("connections.html", name=name)


@app.route("/home/connections", methods=["POST"])
def set_active_connection():
    # expecting {"conn_id":conn_id"}
    global agent_data
    data = json.loads(request.data)
    agent_data.current_connection = data["conn_id"]
    return make_response(
        json.dumps({"result": "Current connection successfully updated"}),
        200
    )


@app.route("/home/proofs", methods=["GET"])
def render_proofs():
    name = os.getenv("ROLE")
    return render_template("proofs.html", name=name)

@app.route("/home/proofs/history", methods=["GET"])
def get_proof_history():
    return make_response(
        json.dumps(ob.get_pres_ex_records()),
        200
    )

@app.route("/request_proof/", methods=["GET"])
def req_proof():
    if not hasActiveConnection():
        return make_response({"code":"failure", "reason":"no active connections"})

    logging.debug("Has active connection :)")
    role=os.getenv("ROLE")
    if role == "flaskvendor":
        request_proof_of_payment()

    elif role == "flaskshipper":
        request_proof_of_ownership()

    return make_response({"code":"success"})

@app.route("/proofs/request", methods=["GET"])
def issue_proof_req():
    if not hasActiveConnection():
        return make_response({"code":"failure", "reason":"no active connections"})

    logging.debug("Has active connection :)")
    role=os.getenv("ROLE")
    if role == "flaskvendor":
        request_proof_of_payment()

    elif role == "flaskshipper":
        request_proof_of_ownership()

    return make_response({"code":"success"})

@app.route("/home/credentials", methods=["GET"])
def render_credentials():
    name = os.getenv("ROLE")

    bank_did = agent_data.bank_did
    vendor_did = agent_data.vendor_did
    shipper_did = agent_data.shipper_did

    this_did_res = ob.get_public_did()

    #todo check if
    if name == "flaskvendor":
        vendor_did = this_did_res['result']['did']
    elif name == "flaskshipper":
        shipper_did = this_did_res['result']['did']
    elif name == "flaskbank":
        bank_did = this_did_res['result']['did']

    return render_template("credentials.html", name=name, vendor_did=vendor_did, bank_did=bank_did, ship_did=shipper_did)

@app.route("/credentials/history", methods=["GET"])
def get_cred_ex_history():
    return make_response(
        json.dumps(ob.get_cred_ex_records()),
        200
    )


@app.route("/status/", methods=["GET"])
def get_status():
    status = ob.get_status()
    return make_response(json.dumps(status), 200)

@app.route("/create_invite/", methods=["GET"])
def make_inv():
    resp = ob.create_invite()
    return make_response(json.dumps(resp["invitation"]), 200)


@app.route("/set_dids", methods=["POST"])
def set_dids():
    global agent_data
    did_dict = request.form.to_dict()
    print(did_dict)

    if "shipper_did" in did_dict.keys():
        agent_data.shipper_did = did_dict["shipper_did"]

    if "bank_did" in did_dict.keys():
        print("bank_did_pres")
        agent_data.bank_did = did_dict["bank_did"]

    if "vendor_did" in did_dict.keys():
        agent_data.vendor_did = did_dict["vendor_did"]

    return make_response({"code":"success"}, 200)


@app.route("/receive_invite/", methods=["POST"])
def rec_inv():
    invdict = request.form.to_dict()
    invite = invdict['invite']
    ob.receive_invite(invite)
    return make_response("invitation", 200)


@app.route("/get_connections/", methods=["GET"])
def get_conns():
    return make_response(json.dumps(ob.get_connections()))

@app.route("/get_active_connections/", methods=["GET"])
def get_active_conns():
    cons = ob.get_connections()
    agents = [
        (x['their_label'], x['connection_id']) for x in cons['results'] if x['state'] == "active"
    ]

    if not agents:
        return make_response(json.dumps({"result": "no active connections"}), 200)

    return make_response(json.dumps({x[0]: x[1] for x in agents}), 200)

    return make_response(json.dumps(ob.get_connections()))


@app.route("/send_message/", methods=["POST"])
def send_msg():
    msgDict = request.form.to_dict()
    message = msgDict['message']
    message = {
        "content": message
    }
    logging.debug("Message contents: %s", message["content"])
    response = ob.send_message(message, agent_data.current_connection)
    print(response)
    return make_response(json.dumps(response), 200)

@app.route("/issue_cred/", methods=["GET"])
def issue_credreq():

    if not hasActiveConnection():
        return make_response({"code":"failure", "reason":"agent has no active connections"})

    logging.debug("Has active connection :)")

    role = os.getenv("ROLE")

    if role == "flaskbank":
        logging.debug("MAJOR STAGE: ISSUEING PAYMENT CRED")
        send_payment_cred_offer(agent_data.current_connection, agent_data.creddef_id)

    elif role == "flaskvendor":
        logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        send_package_cred_offer(agent_data.current_connection, agent_data.creddef_id)

    return make_response({"code":"success", "role": role}, 200)



#### END interface routes

#### START Aries inbound coms
@app.route("/webhooks/topic/connections/", methods=["POST"])
def connections():
    global agent_data
    logging.debug("CONNECTIONS REC")
    data = json.loads(request.data)
    state = data['state']
    initiator = data['initiator']

    if state == "request":
        if initiator == "self":
            logging.debug(f"invitation used by {data['their_label']}")

    if state == "active":
        logging.debug(f"Connection active with {data['their_label']} of did {data['their_did']} with initiator {data['initiator']}")
        if not agent_data.active:
            agent_data.active = True
        agent_data.current_connection = data['connection_id']

    return make_response(json.dumps({"code":"success"}), 200)

@app.route("/webhooks/topic/basicmessages/", methods=["POST"])
def messages():
    data = json.loads(request.data)
    logging.debug("received message : %s", data["content"])
    return make_response(json.dumps({"code":"success"}), 200)

@app.route("/webhooks/topic/issue_credential/", methods=["POST"])
def issue_cred():
    logging.debug("Received cred msg")
    data = json.loads(request.data)
    state = data["state"]
    initiator = data["initiator"]
    credex_id = data["credential_exchange_id"]

    conn_id = data["connection_id"]
    creddef_id = data["credential_definition_id"]
    credex_id = data["credential_exchange_id"]

    credex_details = ob.get_cred_ex_record(credex_id)

    role = None
    if "role" in credex_details:
        role = credex_details["role"]
    elif initiator == "self":
        role = "issuer"

    logging.debug("...with state: %s, intitiator: %s, and id: %s", state, initiator, id)
    logging.debug("With my role: %s", role)

    if state == "request_received" and role == "issuer":

        cred_preview = agent_data.previews[creddef_id]

        if agent_data.agent_role == "flaskvendor":

            cred = {
                "comment": "issuance of payment credential",
                "credential_preview": cred_preview
            }

        elif agent_data.agent_role == "flaskbank":

            cred = {
                "comment": "issuance of package credential",
                "credential_preview": cred_preview
            }
    elif state == "request_received" and role == "holder":


        resp = ob.issue_credential(credex_id, cred)
        print(f"issue cred webhook, conn id {conn_id}")

    return make_response(json.dumps({"code": "success"}), 200)

@app.route("/webhooks/topic/present_proof/", methods=["POST"])
def present_proof():
    data = json.loads(request.data)
    presex_id = data["presentation_exchange_id"]
    state = data["state"]
    logging.debug(f"message recieved thoruhg prsent proof, with creedx_id: {presex_id} and state: {state}")

    #todo: account for role

    if state == "presentation_received":
        logging.debug("received user proof presentation")

        proof = ob.verify_presentation(presex_id)
        logging.debug("Verification result is: %s", proof["verified"])

        ##only do the following if verified == True, leaving as is for the mo
        #if agent_data.agent_role == "flaskvendor":
        #    logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        #    send_package_cred_offer(agent_data.current_connection, agent_data.creddef_id)

    return make_response(json.dumps({"code":"success"}), 200)

@app.route("/webhooks/topic/<topicname>/", methods=["POST", "GET"])
def catch(topicname):
    print("got unhandled request of topic: ", topicname)
    return make_response(json.dumps({"code":"not yet done"}), 501)

def is_verified(presex_id):
    resp = ob.get_pres_ex_details(presex_id)
    if resp['state'] != "verified":
        return False
    else:
        return resp['verified']

def get_genesis_text(ledger_url):
    try:
        ledger_url = ledger_url + "/genesis"
        logging.debug(f"called with url: {ledger_url}")
        response = requests.get(ledger_url)
        logging.debug(response.text)
        return json.loads(response.text)
    except Exception as e:
        print(e)
        pass

def register_did(ledger_url, seed=None, alias=None, role="TRUST_ANCHOR"):
    content = {
        "seed": seed,
        "alias": alias,
        "role": role,
    }
    response = requests.post(ledger_url + "/register", data=json.dumps(content))
    return json.loads(response.text)


def gen_rand_seed():
    name = str(random.randint(100_000, 999_999))
    seed = ("flask_s_000000000000000000000000" + name)[-32:]
    return name, seed


def await_agent(admin_url):
    while True:
        try:
            response = requests.get(admin_url)
            status_code = response.status_code
            print("scode: ", status_code)
            if status_code == 200:
                print("agent is up and running")
                return True
        except Exception as e:
            pass
        time.sleep(2)

def register_schema(name, version, attrs, revocation=False):
    schema = build_schema(name, version, attrs)
    print(schema)
    resp = ob.register_schema(schema)
    print(resp)
    id = resp["schema_id"]
    creddef = {"schema_id": id, "support_revocation": revocation}
    resp = ob.register_creddef(creddef)
    creddef_id = resp["credential_definition_id"]
    global agent_data
    agent_data.creddef_id = creddef_id
    return id, creddef_id

### START hardcoded demo funcs####
def request_proof_of_ownership():

    if not agent_data.vendor_did:
        vendor_did = "HegZx8K7fExo4VKjcw52cX"
    else:
        vendor_did = agent_data.vendor_did

    builder = build_proof_request(name="proof of package ownership", version="1.0")
    req = builder.withAttribute(
        "package_no",
        restrictions=[{"issuer_did":vendor_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":vendor_did}]
    ).withAttribute(
        "address"               ##not sure if her but whatever just a demo
    ).with_conn_id(agent_data.current_connection).build()
    return ob.send_proof_request(req)

def request_proof_of_payment():

    print(agent_data.bank_did)
    if not agent_data.bank_did:
        print("agent data has no bank did")
        bank_did = "Vmc6AeqQQZ8frqF5zPCZtX"
    else:
        bank_did = agent_data.bank_did
    print(bank_did)

    builder = build_proof_request(name="proof of payment", version="1.0")
    req = builder.withAttribute(
        "transaction_id",
        restrictions=[{"issuer_did":bank_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":bank_did}]
    ).withPred(         #todo remove this, just an experimentation with the req preds
        "amount",
        [{"issuer_did":bank_did}],
        ">=",
        14
    ).with_conn_id(agent_data.current_connection).build()
    return ob.send_proof_request(req)

def register_payment_schema(url):
    global agent_data
    attrs = ["transaction_no", "timestamp"]
    schema = {
        "schema_name": "payment_credential",
        "schema_version": "1.0",
        "attributes": ["transaction_no", "timestamp"]
    }
    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id": id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        print(resp)
        agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_package_schema(url):
    global agent_data
    schema = {
        "schema_name": "package_cred",
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp", "status", "shipper_did"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id =  response["schema_id"]
    creddef = {"schema_id":id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def send_package_cred_offer(conn_id, creddef_id):
    global agent_data
    logging.debug("Issue credential to user")

    shipper_did = None
    if not agent_data.shipper_did:
        shipper_did = "placeholder"
    else:
        shipper_did = agent_data.shipper_did

    builder = build_cred(creddef_id)
    builder.with_attribute({"package_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_attribute({"shipper_did": shipper_did}) \
        .with_attribute({"status": "at_shipping-service"}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

def send_payment_cred_offer(conn_id, creddef_id):
    global agent_data

    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"transaction_id": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

### END hardcoded demo funcs ###

def input_json_invite(input_json):
    resp = ob.receive_invite(invite_json=input_json)
    return resp

def output_json_invite():
    global agent_data

    resp = ob.create_invite()
    print(json.dumps(resp["invitation"]))
    agent_data.current_connection = resp["connection_id"]
    return resp["connection_id"]

def await_connection():
    while True:
        if not agent_data.active :
            logging.debug("WAITING FOR CONNECTION")
            time.sleep(2)
        else:
            logging.debug("CONNECTED")
            return True

def flask_proc(host, port, debug=False):
    app.run(host=host, port=port, static_folder=os.path.abspath(os.getcwd() + '/static'))

def hasActiveConnection():
    print("in has active")
    resp = ob.get_connections()
    print("resp is: ", resp)

    if not resp:
        return False

    states = [
        x['state'] for x in resp['results']
    ]

    for state in states:
        if state == 'active':
            logging.debug("true")
            return True
    return False

def getStageAndRole(credex_id):
    return ob.get_cred_ex_record(credex_id)

def main():
    global agent_data ##placeholder

    start_port = int(os.getenv("AGENT_PORT"))
    agent_role = os.getenv("ROLE")
    agent_data.agent_role = agent_role
    host = os.getenv("DOCKERHOST")
    logging.debug("Init controller with role: %s, listenting on port: %s", agent_role, str(start_port))

    if not start_port:
        logging.debug("error: no assigned port")
        sys.exit(-1)
    ##init aries
    name, seed = gen_rand_seed()

    if agent_role is not "flaskuser":               ##the user should not be on the public ledger
        register_did("http://" + host + ":9000", seed, agent_role)

    agent_url = "http://" + host + ":" + str(start_port + 1)
    logging.debug("Agent url: %s", agent_url)
    ob.set_agent_url(agent_url)

    start_aries(start_port, seed, agent_role)
    await_agent(agent_url)

    if agent_role == "flaskbank":
        register_payment_schema(agent_url)

    elif agent_role == "flaskvendor":
        register_package_schema(agent_url)

    connection_id = output_json_invite()
    agent_data.connection_id = connection_id


    app.run(host='0.0.0.0', port=start_port+2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=' %(threadName)s : %(message)s')
    print("PATH IS: ", os.getcwd())
    main()

