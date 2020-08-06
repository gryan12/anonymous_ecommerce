#### START interface routes

from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

webhooks = Blueprint('webhooks', __name__)

@webhooks.route("/webhooks/topic/connections/", methods=["POST"])
def connections():
    logging.debug("CONNECTIONS REC")
    data = json.loads(request.data)
    state = data['state']
    initiator = data['initiator']

    if state == "request":
        if initiator == "self":
            logging.debug(f"invitation used by {data['their_label']}")

    if state == "active":
        logging.debug(f"Connection active with {data['their_label']} of did {data['their_did']} with initiator {data['initiator']}")

        if data['their_label'] == "flaskbank":
            #config.bank_did = data['their_did']
            logging.debug("Connection with BANK agent detected, with their did: %s", data["their_did"])
        elif data['their_label'] == "flaskvendor":
            #config.vendor_did = data['their_did']
            logging.debug("Connection with VENDOR agent detected, with their did: %s", data["their_did"])
        elif data['their_label'] == "flaskshipper":
            #config.shipper_did = data['their_did']
            logging.debug("Connection with SHIPPER agent detected, with their did: %s", data["their_did"])

        if not config.agent_data.active:
            config.agent_data.active = True
        config.agent_data.current_connection = data['connection_id']

    return make_response(json.dumps({"code": "success"}), 200)

@webhooks.route("/webhooks/topic/basicmessages/", methods=["POST"])
def messages():
    data = json.loads(request.data)
    logging.debug("received message : %s", data["content"])
    return make_response(json.dumps({"code":"success"}), 200)

@webhooks.route("/webhooks/topic/issue_credential/", methods=["POST"])
def issue_cred():
    logging.debug("Received cred msg")
    data = json.loads(request.data)
    state = data["state"]
    initiator = data["initiator"]
    creddef_id = data["credential_definition_id"]
    credex_id = data["credential_exchange_id"]
    logging.debug("...with state: %s, intitiator: %s, and id: %s", state, initiator, credex_id)

    if state == "request_received":
        cred_preview = config.agent_data.previews[creddef_id]
        if config.agent_data.agent_role == "flaskvendor":
            cred = {
                "comment": "issuance of payment credential",
                "credential_preview": cred_preview
            }
        elif config.agent_data.agent_role == "flaskbank":
            cred = {
                "comment": "issuance of package credential",
                "credential_preview": cred_preview
            }
        resp = ob.issue_credential(credex_id, cred)

    elif state == "offer_received":
        ob.send_cred_request(credex_id)

    elif state == "credential_received":
        config.agent_data.credentials.append(
            {
                data["connection_id"]: creddef_id
            }
        )

    elif state == "credential_acked":
        logging.debug("Credential stored")

    return make_response(json.dumps({"code": "success"}), 200)

#todo move proof and cred handing logic to their own funcs/objs
@webhooks.route("/webhooks/topic/present_proof/", methods=["POST"])
def present_proof():
    data = json.loads(request.data)
    presex_id = data["presentation_exchange_id"]
    state = data["state"]
    logging.debug(f"message recieved thoruhg prsent proof, with creedx_id: {presex_id} and state: {state}")


    if state == "proposal_received":
        proposal = data["presentation_proposal_dict"]["presentation_proposal"]
        print(proposal)
        creddef_id = proposal["attributes"][0]["cred_def_id"]
        logging.debug("received proposal for proof presentation: ")
        if config.role == "flaskvendor":
            print("config role: ", config.role)
            logging.debug("... at vendor")
            trans.request_proof_of_payment(creddef_id)

    elif state == "presentation_received":
        logging.debug("received user proof presentation")
        proof = ob.verify_presentation(presex_id)
        logging.debug("Verification result is: %s", proof["verified"])


    elif state == "request_received":
        pres_req = data["presentation_request"]
        ref_creds = {}
        req_creds = ob.get_req_creds(presex_id)

        if req_creds:
            for row in sorted(
                    req_creds,
                    key=lambda c: int(c["cred_info"]["attrs"]["timestamp"]),
                    reverse=True,
            ):
                for ref in row["presentation_referents"]:
                    if ref not in ref_creds:
                        ref_creds[ref] = row

            revealed = {}
            for req_attr in pres_req["requested_attributes"]:
                if req_attr in ref_creds:
                    revealed[req_attr] = {
                        "cred_id": ref_creds[req_attr]["cred_info"]["referent"], "revealed": True,
                    }
                else:
                    logging.debug("No credential found in wallet for requested attribute")

            preds = {}
            for req_pred in pres_req["requested_predicates"]:
                if req_pred in ref_creds:
                    preds[req_pred] = {
                        "cred_id": ref_creds[req_pred]["cred_info"]["referent"]
                    }

            proof_pres = {
                "requested_predicates": preds,
                "requested_attributes": revealed,
                "self_attested_attributes": {},
            }

            print(proof_pres)

            ob.send_presentation(proof_pres, presex_id)

    return make_response(json.dumps({"code":"success"}), 200)

@webhooks.route("/webhooks/topic/problem_report/", methods=["POST"])
def handle_problem():
    data = json.loads(request.data)
    logging.debug("received erorr message : %s", data["content"])
    return make_response(json.dumps({"code": "success"}), 200)

@webhooks.route("/webhooks/topic/<topicname>/", methods=["POST", "GET"])
def catch(topicname):
    print("got unhandled request of topic: ", topicname)
    return make_response(json.dumps({"code":"not yet done"}), 501)
