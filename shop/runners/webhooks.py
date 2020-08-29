from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans


# code to handle all inbound notifactions from the aca-py instance.



webhooks = Blueprint('webhooks', __name__)

log = logging.getLogger(__name__)

@webhooks.route("/webhooks/topic/connections/", methods=["POST"])
def connections():
    data = json.loads(request.data)
    state = data['state']
    initiator = data['initiator']

    if state == "request":
        if initiator == "self":
            log.debug(f"invitation used by {data['their_label']}")

    if state == "active":
        log.debug(f"Connection active with {data['their_label']} of did {data['their_did']} with initiator {data['initiator']}")

        if data['their_label'] == "bank":
            log.debug("Connection with BANK agent detected, with their did: %s", data["their_did"])

        elif data['their_label'] == "vendor":
            log.debug("Connection with VENDOR agent detected, with their did: %s", data["their_did"])

        elif data['their_label'] == "shipper":
            log.debug("Connection with SHIPPER agent detected, with their did: %s", data["their_did"])

        if not config.agent_data.active:
            config.agent_data.active = True
        config.agent_data.current_connection = data['connection_id']

    return make_response(json.dumps({"code": "success"}), 200)

@webhooks.route("/webhooks/topic/basicmessages/", methods=["POST"])
def messages():
    data = json.loads(request.data)
    log.debug("received message : %s", data["content"])
    return make_response(json.dumps({"code":"success"}), 200)

@webhooks.route("/webhooks/topic/issue_credential/", methods=["POST"])
def issue_cred():
    data = json.loads(request.data)
    state = data["state"]
    log.debug("issue cred with state: %s", state)
    # ISSUER state
    if state == "proposal_received":
        if config.role == "vendor":
            log.debug("proposal received as vendor")
            product_id = get_cred_proposal_value(data, "product_id")
            amount = get_cred_proposal_value(data, "amount")
            log.debug("Proposal received for payment, for product with ID: %s", product_id)

            config.agent_data.transaction_request = {
                "product": product_id,
            }
            if amount:
                config.agent_data.transaction_request["amount"] = amount
            trans.send_payment_agreement_cred_offer(data["connection_id"], config.agent_data.creddefs["payment_agreement"], product_id)
            config.agent_data.incoming_transaction(product_id)

    elif state == "proposal_sent":
        if config.role == "user":
            config.agent_data.requested_payment_agreement()

    elif state == "offer_received":
        ob.send_cred_request(data["credential_exchange_id"])

    #issuer state
    elif state == "request_received":
        cred_preview = config.agent_data.previews[data["credential_definition_id"]]
        schema_name = trans.get_schema_name(data["credential_definition_id"])

        if config.agent_data.agent_role == "vendor":
            cred = {
                "comment": "issuance of payment credential",
                "credential_preview": cred_preview
            }

        if config.agent_data.agent_role == "user":
            logging.debug("request received as user?")

            if schema_name == "payment_agreement":
                #todo parse
                pretty_print_obj(data)
                config.agent_data.approved_transaction()


        elif config.agent_data.agent_role == "bank":
            cred = {
                "comment": "issuance of package credential",
                "credential_preview": cred_preview
            }


        elif config.agent_data.agent_role == "shipper":
            cred = {
                "comment": "cred offer",
                "credential_preview": cred_preview
            }
        resp = ob.issue_credential(data["credential_exchange_id"], cred)

    elif state == "credential_received":
        #config.agent_data.credentials.append(
        #    {
        #        data["connection_id"]: data["credential_definition_id"]
        #    }
        #)
        log.debug("Stored credential of id: %s", data["credential_definition_id"])

        if config.role == "vendor":
            #todo PARSE PACKAGE NUMBER
            package_no = trans.get_cred_attr_value("package_no", data)
            log.debug("receipt confirmed for package: %s", package_no)
            config.agent_data.receipt_confirmed(package_no)

        elif config.role == "user":
            schema_name = trans.get_schema_name(data["credential_definition_id"])
            print("-=======schema name: ", schema_name)

            if schema_name == "payment_agreement":
                #pretty_print_obj(data)
                amount = get_cred_proposal_value(data, "amount")
                endpoint = get_cred_proposal_value(data, "payment_endpoint")
                ##endparse

                logging.debug("Recevied payment credential for endpoint: %s, and amount: %s", endpoint, amount)
                config.agent_data.received_agreement_cred(amount, endpoint)

            elif schema_name == "payment_credential":
                #pretty_print_obj(data)
                #todo PARSE TRANSACTION_ID
                transaction_id = get_cred_proposal_value(data, "transaction_no")
                logging.debug("Recevied payment t_id: %s", transaction_id)
                config.agent_data.payment_credential_received(transaction_id)

            elif schema_name == "package_cred":
                #todo PARSE PACKAGE NUMBER
                #pretty_print_obj(data)

                package_no = get_cred_proposal_value(data, "package_no")
                logging.debug("Rceived receipt package credential containing package no: %s", package_no)
                config.agent_data.package_credential_received(package_no)

    elif state == "credential_issued":

        schema_name = trans.get_schema_name(data["credential_definition_id"])
        log.debug("Issued credential, of schema name : %s", schema_name)

        if config.role == "bank":
            config.agent_data.issued_payment_credential()

        elif config.role == "shipper":
            config.agent_data.receipt_issued()

        if config.role == "vendor":
            if schema_name == "package_cred":
                pretty_print_obj(data)
                config.agent_data.package_shipped()
            else:
                config.agent_data.approved_transaction()


    return make_response(json.dumps({"code": "success"}), 200)


## todo: use the webhooks to keep track of current states of packages etc
@webhooks.route("/webhooks/topic/present_proof/", methods=["POST"])
def present_proof():
    data = json.loads(request.data)
    presex_id = data["presentation_exchange_id"]
    state = data["state"]
    log.debug(f"message recieved thoruhg prsent proof, with creedx_id: {presex_id} and state: {state}")
    #pretty_print_obj(data)

    if state == "proposal_received":

        proposal = data["presentation_proposal_dict"]["presentation_proposal"]
        pretty_print_obj(data)
        try:
            creddef_id = proposal["attributes"][0]["cred_def_id"]
            log.debug("received proposal for proof presentation: with id: %s", creddef_id)
        except Exception as e:
            print(e)
            return make_response({"code": "error verifying credenial"})

        schema_name = trans.get_schema_name(creddef_id)
        print("schema name; ", schema_name)
        if not schema_name:
            logging.debug("====Error fetching Schema name===")
            return False

        if config.role == "vendor":
            if schema_name:
                #print("vendor dets: ", config.agent_data.transactions)
                if schema_name == "payment_credential":
                    trans.request_proof_of_payment(creddef_id, presex_id)

        elif config.role == "user":
            if schema_name == "received_package":
                log.debug("requesting proof of package dispatch")
                trans.request_proof_of_dispatch(creddef_id, presex_id)

        elif config.role == "bank":
            log.debug("requesting proof of payment agreement")
            trans.request_proof_of_payment_agreement(creddef_id)

        if config.role == "shipper":
            trans.request_proof_of_ownership(creddef_id)

    elif state == "presentation_received":
        proof = ob.verify_presentation(presex_id)
        log.debug("Verification result is: %s", proof["verified"])
       # endpoint = get_received_presentation_values(data, "payment_endpoint")
       # print("===========endpoint: ", endpoint)

    elif state == "presentation_sent":
        name = data["presentation_request"]["name"]
        print("identifiers: ", data["presentation"]["identifiers"])
        identifiers = data["presentation"]["identifiers"][0]
        log.debug("==presentation sent")
        pretty_print_obj(data)

        if config.role == "vendor":
            config.agent_data.receipt_proven()

        elif config.role == "shipper":
            config.agent_data.receipt_proven()

        if config.role == "user":
            if name == "proof of payment" or "payment_credential" in identifiers["schema_id"]:
                config.agent_data.payment_credential_proven()

            elif name == "proof of payment agreement" or "payment_agreement" in identifiers["schema_id"]:
                config.agent_data.payment_agreement_proven()

            elif name == "proof of dispatch" or "package_cred" in identifiers["schema_id"]:
                config.agent_data.package_ownership_proven()

    ## upon receving a request, send a proof presentation
    elif state == "request_received":

        pres_req = data["presentation_request"]
        ref_creds = {}

        # fetch credentials that match from wallet
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
                    log.debug("No credential found in wallet for requested attribute")

            preds = {}
           # for req_pred in pres_req["requested_predicates"]:
           #     if req_pred in ref_creds:
           #         preds[req_pred] = {
           #             "cred_id": ref_creds[req_pred]["cred_info"]["referent"]
           #         }

            proof_pres = {
                "requested_predicates": preds,
                "requested_attributes": revealed,
                "self_attested_attributes": {},
            }

            ob.send_presentation(proof_pres, presex_id)

    # proof result is True
    elif state == "verified":
        log.debug("Verified")
        if config.role == "vendor":
            if data["verified"] == "true":
                log.debug("payment proven")
                transaction_id = get_received_presentation_values(data, "transaction_no")
                log.debug("=========transaction id: %s", transaction_id)

                config.agent_data.payment_proven(transaction_id)

        elif config.role == "user":
            if data["verified"] == "true":
                log.debug("Receipt proven")
                ##todo confirm
                package_no = get_received_presentation_values(data, "package_no")
                config.agent_data.package_receipt_validated(package_no)

        elif config.role == "bank":
            if data["verified"] == "true":
                log.debug("Receipt proven")
                endpoint = get_received_presentation_values(data, "payment_endpoint")
                print("===========endpoint: ", endpoint)
                config.agent_data.validate_agreement(endpoint)


        elif config.role == "shipper":
            if data["verified"] == "true":
                log.debug("Receipt proven")
                package_no = get_received_presentation_values(data, "package_no")
                log.debug("=========Package no: %s", package_no)
                config.agent_data.ownership_validated(package_no)

    return make_response(json.dumps({"code":"success"}), 200)

@webhooks.route("/webhooks/topic/problem_report/", methods=["POST"])
def handle_problem():
    print(request.headers)
    print(request.data)
    return make_response(json.dumps({"code": "success"}), 200)


@webhooks.route("/webhooks/topic/<topicname>/", methods=["POST", "GET"])
def catch(topicname):
    print("got unhandled request of topic: ", topicname)
    return make_response(json.dumps({"code":"not yet done"}), 501)

# for aesthetic printing of json objects
def pretty_print_obj(json_dict):
    pretty = json.dumps(json_dict, indent=4)
    print(pretty)
    return pretty


# get the value of a given attr_name from a proof proposal, a json object
def get_proposal_value(proposal, attr_name):
    if "presentation_proposal_dict" in proposal:
        attrs = proposal["presentation_proposal_dict"]["presentation_proposal"]["attributes"]
        for attr in attrs:
            if attr["name"] == attr_name:
                return attr["value"]


# get the value of a given attr_name from a crdential proposal, a json object
def get_cred_proposal_value(proposal, attr_name):
    if "credential_proposal_dict" in proposal:
        attrs = proposal["credential_proposal_dict"]["credential_proposal"]["attributes"]
        for attr in attrs:
            if attr["name"] == attr_name:
                return attr["value"]
    return False

def get_received_presentation_values(proposal, attr_name):
    if "presentation" in proposal:
        if "requested_proof" in proposal["presentation"]:
            for attr in proposal["presentation"]["requested_proof"]["revealed_attrs"]:
                if attr_name in attr:
                    print(attr_name)
                    return proposal["presentation"]["requested_proof"]["revealed_attrs"][attr]["raw"]
    return False