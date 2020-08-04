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
from runners.support.creds import build_cred, build_proof_request, build_schema
import runners.support.settings as config

def request_proof_of_ownership():

    if not config.agent_data.vendor_did:
        vendor_did = "HegZx8K7fExo4VKjcw52cX"
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


def request_proof_of_payment():
    print(config.agent_data.bank_did)
    if not config.agent_data.bank_did:
        print("agent data has no bank did")
        bank_did = "Vmc6AeqQQZ8frqF5zPCZtX"
    else:
        bank_did = config.agent_data.bank_did
    print(bank_did)

    builder = build_proof_request(name="proof of payment", version="1.0")
    req = builder.withAttribute(
        "transaction_no",
        restrictions=[{"issuer_did":bank_did}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"issuer_did":bank_did}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)


def send_payment_cred_offer(conn_id, creddef_id):
    #global config.agent_data

    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"transaction_no": "asdf1234"}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

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

def send_package_cred_offer(conn_id, creddef_id):
    logging.debug("Issue credential to user")

    if not config.agent_data.shipper_did:
        shipper_did = "placeholder"
    else:
        shipper_did = config.agent_data.shipper_did

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


def register_payment_schema(url):
    #global config.agent_data
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
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_package_schema(url):
    #global config.agent_data
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

def register_receipt_schema(url):
    schema = {
        "schema_name": "receipt_of_package",
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp", "status"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id =  response["schema_id"]
    creddef = {"schema_id":id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]
def register_payment_schema(url):
    #global config.agent_data
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
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_package_schema(url):
    #global config.agent_data
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

def register_receipt_schema(url):
    schema = {
        "schema_name": "receipt_of_package",
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp", "status"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id =  response["schema_id"]
    creddef = {"schema_id":id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_schema(name, version, attrs, revocation=False):
    schema = build_schema(name, version, attrs)
    print(schema)
    resp = ob.register_schema(schema)
    print(resp)
    id = resp["schema_id"]
    creddef = {"schema_id": id, "support_revocation": revocation}
    resp = ob.register_creddef(creddef)
    creddef_id = resp["credential_definition_id"]
    ##global config.agent_data
    config.agent_data.creddef_id = creddef_id
    return id, creddef_id
