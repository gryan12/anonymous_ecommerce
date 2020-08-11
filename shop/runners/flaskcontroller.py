import json
import logging
import requests
import random
from threading import Thread
import os
import sys
import time
from flask import Flask, request, make_response, render_template, redirect

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
from runners.agent_proc import start_aries
from runners.webhooks import webhooks
import runners.support.settings as config
import runners.transaction_logic as trans

path = os.path.join(os.getcwd(), "shop/runners/static")
app = Flask(__name__, static_folder=path)
app.register_blueprint(webhooks)

##ugly but placeholder for db
#agent_data = Data()
##det endpoints
##============================================================================
#Call to propose for a proof.
#If the user agent, then proposing proof of payment OR
#proposing proof of
@app.route("/payment/propose_proof/", methods=["GET"])
def prop_proof():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose proof of payment
    if config.role == "flaskuser":
        logging.debug("proposing proof of payment")
        payment_creddef = trans.get_payment_creddefid()
        if not payment_creddef:
            return make_response({"code": "Do not have correct credential"})

        trans.propose_proof_of_payment(config.agent_data.current_connection, payment_creddef)

    return make_response({"code": "received"})

@app.route("/payment/propose_proof/agreement", methods=["GET"])
def prop_agree_proof():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("proposing proof of purchase agreement")
    agreement_creddef = trans.get_creddefid("payment_agreement")
    trans.propose_proof_of_payment_agreement(config.agent_data.current_connection, agreement_creddef)
    return make_response({"code": "received"})

@app.route("/shop/dispatch/propose_proof/ownership", methods=["GET"])
def prop_prove_ownership():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("proposing proof of package ownership")
    ownership_creddef = trans.get_creddefid("package_cred")
    trans.propose_proof_of_ownership(config.agent_data.current_connection, ownership_creddef)
    return make_response({"code": "received"})


@app.route("/credentials/propose/", methods=["GET"])
def prop_cred():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose payment credential
    if config.role == "flaskuser":
        logging.debug("proposing payment agreement credential")
        payment_creddef = trans.send_payment_agreement_proposal()

    return make_response({"code": "received"})

@app.route("/shop/request_purchase/", methods=["GET"])
def req_purchase():

    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    if config.role != "flaskuser":
        make_response({"code": "not avialable for this agent"}, 500)

    trans.send_payment_agreement_proposal()

    return make_response({"code": "received"})


@app.route("/shop/received_package/", methods=["GET"])
def received_package():

    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})
    if config.role != "flaskshipper":
        make_response({"code": "not avialable for this agent"}, 500)

    creddef_id = config.agent_data.creddefs["received_package"]
    trans.send_package_receipt_cred_offer(config.agent_data.current_connection, creddef_id)

    return make_response({"code": "received"})

@app.route("/shop/dispatch/", methods=["GET"])
def ready_for_dispatch():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose proof of payment
    if config.role != "flaskvendor":
        return make_response({"code":"action unavailable for this demo agent"}, 500)

    logging.debug("proposing proof of package status")
    dispatch_creddef = trans.get_creddefid("received_package")
    if not dispatch_creddef:
        return make_response({"code": "Do not have correct credential"})

    trans.propose_proof_of_dispatch(config.agent_data.current_connection, dispatch_creddef)

    return make_response({"code": "received"})

##================================================================
##### START interface routes
@app.route("/home/", methods=["GET"])
def render_interface():
    name = os.getenv("ROLE")
    if config.agent_data.has_public:
        did = get_public_did()
        return render_template("interface.html", name=name, did=did)
    else:
        return render_template("interface.html", name=name)



##connections
@app.route("/home/connections", methods=["GET"])
def render_connections():
    name = os.getenv("ROLE")
    return render_template("connections.html", name=name)


@app.route("/home/connections", methods=["POST"])
def set_active_connection():
    data = json.loads(request.data)
    config.agent_data.current_connection = data["conn_id"]

    return make_response(
        json.dumps({"result": "Current connection successfully updated"}),
        200
    )


##proofs
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
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("Has active connection :)")
    role=os.getenv("ROLE")
    if role == "flaskvendor":
        trans.request_proof_of_payment()

    elif role == "flaskshipper":
        trans.request_proof_of_ownership()

    return make_response({"code": "success"})

@app.route("/proofs/request", methods=["GET"])
def issue_proof_req():
    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("Has active connection :)")
    role=os.getenv("ROLE")
    if role == "flaskvendor":
        trans.request_proof_of_payment()

    elif role == "flaskshipper":
        trans.request_proof_of_ownership()

    return make_response({"code":"success"})





@app.route("/home/credentials", methods=["GET"])
def render_credentials():
    name = os.getenv("ROLE")

    bank_did = config.agent_data.bank_did
    vendor_did = config.agent_data.vendor_did
    shipper_did = config.agent_data.shipper_did

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

@app.route("/credentials", methods=["GET"])
def get_creds():
    return make_response(
        json.dumps(ob.get_credentials()),
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
    did_dict = request.form.to_dict()
    print(did_dict)

    if "shipper_did" in did_dict.keys():
        if did_dict["shipper_did"]:
            config.agent_data.shipper_did = did_dict["shipper_did"]

    if "bank_did" in did_dict.keys():
        if did_dict["bank_did"]:
            config.agent_data.bank_did = did_dict["bank_did"]

    if "vendor_did" in did_dict.keys():
        if did_dict["vendor_did"]:
            config.agent_data.vendor_did = did_dict["vendor_did"]

    return redirect(request.referrer)


@app.route("/receive_invite/", methods=["POST"])
def rec_inv():
    invdict = request.form.to_dict()
    invite = invdict['invite']
    ob.receive_invite(invite)
    return redirect(request.referrer)


@app.route("/connections/current/", methods=["POST"])
def set_current_conn():
    print(request.headers)
    data = request.json
    print(data)
    if "selected_connection" in data:
        if data["selected_connection"] is not None:
            config.agent_data.current_connection = data["selected_connection"]
    return redirect(request.referrer)

@app.route("/get_connections/", methods=["GET"])
def get_conns():
    r = make_response(json.dumps(ob.get_connections()))
    r.mimetype ="application/json"
    return r

@app.route("/get_active_connections/", methods=["GET"])
def get_active_conns():
    cons = ob.get_connections()
    agents = [
        (x['their_label'], x['connection_id']) for x in cons['results'] if x['state'] == "active"
    ]

    if not config.agent_data.current_connection:
        current = "None"
    else:
        current= config.agent_data.current_connection

    conn_details = ob.get_connection_details(current)
    if "their_label" in conn_details:
        their_label = conn_details['their_label']
        agents.append(("current_connection", their_label))

    if not agents:
        return make_response(json.dumps({"result": "no active connections"}), 200)

    r = make_response(json.dumps({x[0]: x[1] for x in agents}), 200)
    r.mimetype = "application/json"
    return r



@app.route("/send_message/", methods=["POST"])
def send_msg():
    msgDict = request.form.to_dict()
    message = msgDict['message']
    message = {
        "content": message
    }
    logging.debug("Message contents: %s", message["content"])
    response = ob.send_message(message, config.agent_data.current_connection)
    print(response)
    return make_response(json.dumps(response), 200)

@app.route("/issue_cred/", methods=["GET"])
def issue_credreq():

    if not hasActiveConnection():
        return make_response({"code": "failure", "reason": "agent has no active connections"})

    role = os.getenv("ROLE")

    #creddef_ids = ob.get_creddef_id_by_name["package_cred"]
    #if "credential_definition_ids" in creddef_ids:
    #    if creddef_ids["credential_definition_ids"]:
    #        creddef_id = creddef_ids["credential_definition_ids"][0]

    if role == "flaskbank":
        logging.debug("MAJOR STAGE: ISSUeING PAYMENT CRED")
        trans.send_payment_cred_offer(config.agent_data.current_connection, config.agent_data.creddef_id)

    elif role == "flaskvendor":
        logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        trans.send_package_cred_offer(config.agent_data.current_connection, config.agent_data.creddefs["package_cred"])

    elif role == "flaskshipper":
        logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        trans.send_package_receipt_cred_offer(config.agent_data.current_connection, config.agent_data.creddef_id)

    return make_response({"code":"success", "role": role}, 200)

##### END interface routes

#general funcs
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

    config.agent_data.has_public = True

    try:
        resp = json.loads(response.text)
    except json.JSONDecodeError as e:
        print(response.headers)
        logging.debug("ERROR REGISTERING DID WITH THE LEDGER")
        sys.exit(-1)
    return json.loads(response.text)


def gen_rand_seed():
    name = str(random.randint(100_000, 999_999))
    seed = ("flask_s_000000000000000000000000" + name)[-32:]
    return name, seed

##end funcs

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

def input_json_invite(input_json):
    resp = ob.receive_invite(invite_json=input_json)
    return resp

def output_json_invite():
    resp = ob.create_invite()
    config.agent_data.current_connection = resp["connection_id"]
    return resp["connection_id"]


def await_connection():
    while True:
        if not config.agent_data.active :
            logging.debug("WAITING FOR CONNECTION")
            time.sleep(2)
        else:
            logging.debug("CONNECTED")
            return True

def get_public_did():
    resp = ob.get_public_did()
    res = resp["result"]
    if "did" in res:
        return res["did"]
    else:
        return None


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
    start_port = int(os.getenv("AGENT_PORT"))
    agent_role = os.getenv("ROLE")
    config.agent_data.agent_role = agent_role
    host = os.getenv("DOCKERHOST")

    ledger_url = os.getenv("LEDGER_URL")
    if not ledger_url:
        ledger_url = "http://" + host + ":9000"

    logging.debug("Init controller with role: %s, listenting on port: %s", agent_role, str(start_port))

    if not start_port:
        logging.debug("error: no assigned port")
        sys.exit(-1)

    ##init aries
    name, seed = gen_rand_seed()

    if agent_role != "flaskuser":               ##the user should not be on the public ledger
        register_did(ledger_url, seed, agent_role)

    agent_url = "http://" + host + ":" + str(start_port + 1)
    logging.debug("Agent url: %s", agent_url)
    ob.set_agent_url(agent_url)

    start_aries(start_port, seed, agent_role)
    await_agent(agent_url)

    if agent_role == "flaskbank":
        trans.register_payment_schema(agent_url)

    if agent_role == "flaskshipper":
        trans.register_receipt_schema(agent_url)

    elif agent_role == "flaskvendor":
        trans.register_package_schema(agent_url)
        trans.register_payment_agreement_schema(agent_url)

    if agent_role != "flaskuser":

        upper_role = os.getenv("ROLE").upper()
        pub_did_resp = ob.get_public_did()

        did = pub_did_resp["result"]["did"]
        logging.debug("pub did is: %s", did)

        os.environ[upper_role] = did
        logging.debug("set env for public did of: %s as %s", upper_role, did)


    connection_id = output_json_invite()
    config.agent_data.connection_id = connection_id


    app.run(host='0.0.0.0', port=start_port+2)

if __name__ == "__main__":
    config.setup()
    logging.basicConfig(level=logging.DEBUG, format=' %(threadName)s : %(message)s')
    main()

