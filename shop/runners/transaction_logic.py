import json
import logging
import requests
import random
from threading import Thread
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
from runners.support.creds import build_cred, build_proof_request, build_schema, build_credential_proposal, build_proof_proposal
import runners.support.settings as config



#### Stage 1: purchase request

def send_payment_agreement_proposal():
    offer_json = build_credential_proposal(
        comment= "request for payment agreement credential",
        schema_name= "payment agreement",
        issuer_did= config.current_connection
    )
    resp = ob.send_cred_proposal(offer_json)
    print("response to payment proposal:", resp)
    return resp


def register_payment_agreement_schema(url):
    schema = {
        "schema_name": "payment_agreement",
        "schema_version": "1.0",
        "attributes": ["amount", "timestamp", "endpoint"]
    }
    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id": id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]


def send_payment_agreement_cred_offer(conn_id, creddef_id):
    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"transaction_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)


def refuse_payment_agreement(conn_id, creddef_id):
    #todo: return a problem report if vendor cant/wont sell
    return None


#### Stage 2: Payment;
def register_payment_schema(url):
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
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]


def send_payment_cred_offer(conn_id, creddef_id):
    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"transaction_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)


def request_proof_of_payment():

    if not config.agent_data.bank_did:
        return {"error": "did not set"}
    else:
        bank_did = config.agent_data.bank_did

    builder = build_proof_request(name="proof of payment", version="1.0")
    req = builder.withAttribute(
        "transaction_no",
        restrictions=[{"issuer_did":bank_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":bank_did}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)


def propose_proof_of_payment(connection_id, cred_def_id=None):
    proposal = build_proof_proposal(
        "proof_of_payment"
    ).withAttribute(
        "transaction_id",
        cred_def_id,
    ).withAttribute(
        "timestamp",
        cred_def_id
    ).build(connection_id, "wanna prove payhment")

    ob.send_proof_proposal(proposal)


####END Stage 2

####START Stage 3: Package ownership

def register_package_schema(url):
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
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def send_package_cred_offer(conn_id, creddef_id):
    logging.debug("Issue credential to user")

    if not config.agent_data.shipper_did:
        logging.debug("shipper did not set")

        return {"error": "did not set"}
    else:
        shipper_did = config.agent_data.shipper_did

    logging.debug("shipper did is: %s", shipper_did)
    builder = build_cred(creddef_id)


    builder.with_attribute({"package_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_attribute({"shipper_did": shipper_did}) \
        .with_attribute({"status": "at_shipping-service"}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)


def request_proof_of_ownership():

    if not config.agent_data.vendor_did:
        return {
            "error": "vendor did not known"
        }
    else:
        vendor_did = config.agent_data.vendor_did


    builder = build_proof_request(name="proof of package ownership", version="1.0")
    req = builder.withAttribute(
        "package_no",
        restrictions=[{"issuer_did":vendor_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":vendor_did}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)

####END Stage 3

####START Stage 4: receipt of package
def register_receipt_schema(url):
    schema = {
        "schema_name": "receipt_of_package",
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp", "status"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id":id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]


def send_package_receipt_cred_offer(conn_id, creddef_id):
    logging.debug("Issue receipt credential to vendor")
    builder = build_cred(creddef_id)
    builder.with_attribute({"package_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package-receipt credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)


def request_proof_of_receipt():
    builder = build_proof_request(name="proof of shipped package", version="1.0")
    req = builder.withAttribute(
        "package_no",
        restrictions=[{"issuer_did":config.agent_data.shipper_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":config.agent_data.shipper_did}]
    ).withAttribute(
        "status",
        restrictions=[{"issuer_did": config.agent_data.shipper_did}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)


##helper
def register_schema(name, version, attrs, revocation=False):
    schema = build_schema(name, version, attrs)
    resp = ob.register_schema(schema)
    id = resp["schema_id"]
    creddef = {"schema_id": id, "support_revocation": revocation}
    resp = ob.register_creddef(creddef)
    creddef_id = resp["credential_definition_id"]
    config.agent_data.creddef_id = creddef_id
    return id, creddef_id

##placeholder for
def lookup_did(agent_name):

    if agent_name =="flaskshipper":
        print("shipper")
        if config.agent_data.shipper_did:
            print("returning config")
            return config.agent_data.shipper_did
        else:
            print("returning lookup")
            config.agent_data.shipper_did = read_didenv(agent_name)

    elif agent_name =="flaskvendor":
        if config.agent_data.vendor_did:
            return config.agent_data.vendor_did
        else:
            config.agent_data.vendor_did = read_didenv(agent_name)

    elif agent_name=="flaskbank":
        if config.agent_data.bank_did:
            return config.agent_data.bank_did
        else:
            config.agent_data.bank_did = read_didenv(agent_name)
    else:
        return None


def read_didenv(agent_name):
    env_did = os.getenv(agent_name.upper())
    if env_did:
        logging.debug("Parsed env did for %s of %s", agent_name, env_did)
    return env_did

