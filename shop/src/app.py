import json
import requests
import random
import os
import sys
import time

from flask import Flask, request, make_response, render_template, redirect, url_for

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.support.outbound_routing as ob
from src.agent_proc import start_aries
from src.blueprints.webhooks import webhooks
from src.blueprints.proofs import proofs
from src.blueprints.credentials import credentials
from src.blueprints.connections import connections
from src.blueprints.shop import shop
import src.support.settings as config
import src.transaction_logic as trans
import logging

path = os.path.join(os.getcwd(), "shop/src/static")
app = Flask(__name__, static_folder=path)
app.register_blueprint(webhooks)
app.register_blueprint(proofs)
app.register_blueprint(connections)
app.register_blueprint(credentials)
app.register_blueprint(shop)

flask_log = logging.getLogger('werkzeug')
flask_log.disabled = True
app.logger.disabled = True

logging.basicConfig(level=logging.DEBUG, format=' --- %(name)s : %(message)s')
log = logging.getLogger(__name__)


#This file contains the routes for rendering html templates, and for initialising
#  the flask application, and functions for interfacing with an Indy ledger

@app.route("/", methods=["GET"])
def red():
    return redirect(url_for('shop.render_shop_actions'))

@app.route("/home/", methods=["GET"])
def render_interface():
    name = os.getenv("ROLE").capitalize()
    if config.agent_data.has_public:
        did = get_public_did()
        return render_template("interface.html", name=name, did=did)
    else:
        return render_template("interface.html", name=name)

@app.route("/home/connections", methods=["GET"])
def render_connections():
    name = os.getenv("ROLE").capitalize()
    return render_template("connections.html", name=name)

@app.route("/home/connections", methods=["POST"])
def set_active_connection():
    data = json.loads(request.data)
    config.agent_data.current_connection = data["conn_id"]

    return make_response(
        json.dumps({"result": "Current connection successfully updated"}),
        200
    )
@app.route("/home/proofs", methods=["GET"])
def render_proofs():
    name = os.getenv("ROLE").capitalize()
    return render_template("proofs.html", name=name)

@app.route("/home/credentials", methods=["GET"])
def render_credentials():
    name = os.getenv("ROLE").capitalize()
    return render_template("credentials.html", name=name)

@app.route("/status/", methods=["GET"])
def get_status():
    status = ob.get_status()
    return make_response(json.dumps(status), 200)

# handle outbound messages.
@app.route("/send_message/", methods=["POST"])
def send_msg():
    msgDict = request.form.to_dict()
    message = msgDict['message']
    message = {
        "content": message
    }
    log.debug("Message contents: %s", message["content"])
    response = ob.send_message(message, config.agent_data.current_connection)
    return make_response(json.dumps(response), 200)

##### END interface routes

## perform a NYM transaction
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
        log.debug("ERROR REGISTERING DID WITH THE LEDGER")
        sys.exit(-1)
    return json.loads(response.text)


def gen_rand_seed():
    name = str(random.randint(222_222, 888_888))
    seed = ("flask_s_000000000000000000000000" + name)[-32:]
    return name, seed

# ping agnet until it responds
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
        if not config.agent_data.active:
            log.debug("WAITING FOR CONNECTION")
            time.sleep(2)
        else:
            log.debug("CONNECTED")
            return True
def get_public_did():
    resp = ob.get_public_did()
    res = resp["result"]
    if "did" in res:
        return res["did"]
    else:
        return None


def hasActiveConnection():
    resp = ob.get_connections()
    if not resp:
        return False
    states = [
        x['state'] for x in resp['results']
    ]

    for state in states:
        if state == 'active':
            log.debug("true")
            return True
    return False

def getStageAndRole(credex_id):
    return ob.get_cred_ex_record(credex_id)

def main():
    # get agent details from osenv, set in start_shop_agent script
    start_port = int(os.getenv("AGENT_PORT"))
    agent_role = os.getenv("ROLE")
    config.agent_data.agent_role = agent_role
    host = os.getenv("DOCKERHOST")

    if os.getenv("AGENT_RUNNING"):
        log.debug("AGENT IS ALREADY RUNNING")

    ledger_url = os.getenv("LEDGER_URL")
    if not ledger_url:
        ledger_url = "http://" + host + ":9000"

    log.debug("Init controller with role: %s, listenting on port: %s", agent_role, str(start_port))

    if not start_port:
        log.debug("error: no assigned port")
        sys.exit(-1)

    ##init aries
    name, seed = gen_rand_seed()

    ## the user should not have a public did
    if agent_role != "user":
        register_did(ledger_url, seed, agent_role)

    ## aca-py instance endpoint
    agent_url = "http://" + host + ":" + str(start_port + 1)
    log.debug("Agent url: %s", agent_url)
    ob.set_agent_url(agent_url)

    start_aries(start_port, seed, agent_role)
    await_agent(agent_url)

    ## regiter role-specific schema
    if agent_role == "bank":
        trans.register_payment_schema(agent_url)

    if agent_role == "shipper":
        trans.register_receipt_schema(agent_url)

    elif agent_role == "vendor":
        trans.register_package_schema(agent_url)
        trans.register_payment_agreement_schema(agent_url)

    ## if registered a public did:
    if agent_role != "user":
        upper_role = os.getenv("ROLE").upper()
        pub_did_resp = ob.get_public_did()

        did = pub_did_resp["result"]["did"]
        log.debug("pub did is: %s", did)

        os.environ[upper_role] = did
        log.debug("set env for public did of: %s as %s", upper_role, did)

        connection_id = output_json_invite()
        config.agent_data.connection_id = connection_id

    app.run(host='0.0.0.0', port=start_port+2, debug=False)

if __name__ == "__main__":
    config.setup()
    main()
