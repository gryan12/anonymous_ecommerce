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
##todo the idea here is that initiating purchase of a prpduct would intitiate
## a credential proposal that incldues the value to be paid, the listing id,
## and an endpoint. The vendor cna then refuse or accept a requet to purchase,
## with the latter involving issueing a credential of the relevant amount.
## any potential dispute could be accomplised over resending a credential offer.


CRED_NAMES = [
    "payment_agreement",
    "payment_credential",
    "package_cred",
    "received_package",
]

##User
#User -> Vendor

#todo amount
def send_payment_agreement_proposal(product_id):

    config.agent_data.update_product_id(product_id)

    proposal = {
       "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
       "attributes": [
            {
                "name": "product_id",
                "value": product_id
            },
        ]
    }
    offer_json = build_credential_proposal(
        config.agent_data.current_connection,
        comment="request for payment agreement credential",
        schema_name="payment agreement",
        prop_schema=proposal
    )

    resp = ob.send_cred_proposal(offer_json)
    return resp

def send_payment_agreement_cred_offer(conn_id, creddef_id, product_id, value="50", endpoint="placeholder_endpoint"):
    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"payment_endpoint": endpoint}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_attribute({"amount": value}) \
        .with_attribute({"product_id": product_id}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("purchase request")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

#User -> Bank
def propose_proof_of_payment_agreement(connection_id, cred_def_id):
    proposal = build_proof_proposal(
        "proof_of_payment_agreement"
    ).withAttribute(
        "payment_endpoint",
        cred_def_id,
    ).withAttribute(
        "amount",
        cred_def_id
    ).withAttribute(
        "timestamp",
        cred_def_id
    ).build(connection_id, comment="proof of payment agreement")
    return ob.send_proof_proposal(proposal)

#User -> Vendor
def propose_proof_of_payment(connection_id, cred_def_id=None):
    proposal = build_proof_proposal(
        "proof_of_payment"
    ).withAttribute(
        "transaction_no",
        cred_def_id,
    ).withAttribute(
        "timestamp",
        cred_def_id
    ).build(connection_id, comment="wanna prove payhment")
    return ob.send_proof_proposal(proposal)


def refuse_payment_agreement(conn_id, creddef_id):
    #todo: return a problem report if vendor cant/wont sell
    return None

def request_proof_of_payment_agreement(creddef_id = None):
    if not creddef_id:
        return {"error": "no creddef id"}

    builder = build_proof_request(name="proof of payment agreement", version="1.0")
    req = builder.withAttribute(
        "payment_endpoint",
        restrictions=[{"cred_def_id": creddef_id}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"cred_def_id": creddef_id}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)

#### Stage 2: Payment;
#Bank -> User
def send_payment_cred_offer(conn_id, creddef_id):

    transaction_no = gen_transaction_id()
    config.agent_data.transaction_no = transaction_no

    logging.debug("Issue credential to user")
    builder = build_cred(creddef_id)
    builder.with_attribute({"transaction_no": transaction_no}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("payment credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)


#stage 3: proving payment

#Vendor -> User
def request_proof_of_payment(creddef_id = None, presex_id=None):

    if not creddef_id:
        if not config.agent_data.payment_creddef:
            return {"error": "no creddef id"}
        else:
            creddef_id = config.agent_data.payment_creddef

    builder = build_proof_request(name="proof of payment", version="1.0")
    req = builder.withAttribute(
        "transaction_no",
        restrictions=[{"cred_def_id": creddef_id}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"cred_def_id": creddef_id}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req, presex_id)


##### PROOF PACKAGE AT SHIPPING SERVICE ######

#Vendor -> User
def propose_proof_of_dispatch(connection_id, cred_def_id):
    proposal = build_proof_proposal(
        "proof_of_dispatch"
    ).withAttribute(
        "package_no",
        cred_def_id,
    ).withAttribute(
        "timestamp",
        cred_def_id
    ).build(connection_id, comment="Package is at shipping service")
    return ob.send_proof_proposal(proposal)

#User -> Vendor
def request_proof_of_dispatch(creddef_id = None, presex_id=None):

    if not creddef_id:
        if not config.payment_creddef:
            return {"error": "no creddef id"}
        else:
            creddef_id = config.agent_data.payment_creddef

    builder = build_proof_request(name="proof of dispatch", version="1.0")
    req = builder.withAttribute(
        "timestamp",
        restrictions=[{"cred_def_id": creddef_id}]
    ).withAttribute(
        "package_no",
        restrictions=[{"cred_def_id": creddef_id}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req, presex_id)


##############################################

####END Stage 2
####START Stage 3: Package ownership

#Vendor -> user
def send_package_cred_offer(conn_id, creddef_id):
    logging.debug("Issue credential to user")

    package_no = gen_package_no()
    config.agent_data.update_package_no(package_no)
    builder = build_cred(creddef_id)

    builder.with_attribute({"package_no": package_no}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_attribute({"status": "dispatched_to_shipping_service"}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

#User -> Shipper
def propose_proof_of_ownership(conn_id, creddef_id):
    builder = build_proof_proposal("proof of package ownership")
    req = builder.withAttribute(
        "package_no",
        cred_def_id=creddef_id
    ).withAttribute(
        "timestamp",
        cred_def_id=creddef_id
    ).build(conn_id, comment="proof of package ownership")
    return ob.send_proof_proposal(req)


#Shipper -> User
def request_proof_of_ownership(creddef_id):
    builder = build_proof_request(name="proof of package ownership", version="1.0")
    req = builder.withAttribute(
        "package_no",
        restrictions=[{"cred_def_id": creddef_id}]
    ).withAttribute(
        "timestamp",
        restrictions=[{"cred_def_id": creddef_id}]
    ).with_conn_id(config.agent_data.current_connection).build()
    return ob.send_proof_request(req)

####END Stage 3
####START Stage 4: receipt of package
#Shipper -> Vendor
def send_package_receipt_cred_offer(conn_id, creddef_id, package_no):
    logging.debug("Issue receipt credential to vendor")
    builder = build_cred(creddef_id)
    builder.with_attribute({"package_no": package_no}) \
        .with_attribute({"timestamp": str(int(time.time()))}) \
        .with_type("did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview") \
        .with_conn_id(conn_id)

    offer_req = builder.build_offer("package-receipt credential issuance")
    config.agent_data.previews[creddef_id] = builder.build_preview()
    return ob.send_cred_offer(offer_req)

#User -> Vendor
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

#Vendor -> User
def propose_proof_of_package_status(connection_id, cred_def_id=None):
    proposal = build_proof_proposal(
        "proof_of_package_status"
    ).withAttribute(
        "package_no",
        cred_def_id=cred_def_id,
    ).withAttribute(
        "timestamp",
        cred_def_id=cred_def_id,
    ).build(connection_id, comment="Package is at shipping service")
    return ob.send_proof_proposal(proposal)

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


## need a way of keeping track who is for what
def get_agreement_creddefid():
    credentials = ob.get_credentials()
    res = credentials["results"]
    print("results of payment credf: ", res)
    payment_creds = [x for x in res if "payment_agreement" in x["schema_id"]]
    print("payment creds", res)
    if payment_creds:
        return payment_creds[0]["cred_def_id"]
    else:
        return None

def get_creddefid(schema_name):
    credentials = ob.get_credentials()
    res = credentials["results"]
    print("results of payment credf: ", res)
    payment_creds = [x for x in res if schema_name in x["schema_id"]]
    print("payment creds", res)
    if payment_creds:
        return payment_creds[0]["cred_def_id"]


def get_payment_creddefid():
    credentials = ob.get_credentials()
    res = credentials["results"]
    payment_creds = [x for x in res if "payment_credential" in x["schema_id"]]
    if payment_creds:
        return payment_creds[0]["cred_def_id"]

def get_package_creddefid():
    credentials = ob.get_credentials()
    res = credentials["results"]
    package_creds = [x for x in res if "package_cred" in x["schema_id"]]
    if package_creds:
        return package_creds[0]["cred_def_id"]

def register_payment_agreement_schema(url):
    schema_name = "payment_agreement"
    schema = {
        "schema_name": schema_name,
        "schema_version": "1.0",
        "attributes": ["amount", "timestamp", "payment_endpoint", "product_id"]
    }
    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id": id, "support_revocation": False}
    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        config.agent_data.creddefs[schema_name] = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

#schema reg
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
        config.agent_data.payment_creddef = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_package_schema(url):
    schema_name = "package_cred"
    schema = {
        "schema_name": schema_name,
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp", "status"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id":id, "support_revocation": False}

    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        config.agent_data.creddefs[schema_name] = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def register_receipt_schema(url):
    schema_name = "received_package"
    schema = {
        "schema_name": schema_name,
        "schema_version": "1.0",
        "attributes": ["package_no", "timestamp"]
    }

    response = ob.post(url + "/schemas", data=schema)
    id = response["schema_id"]
    creddef = {"schema_id": id, "support_revocation": False}

    resp = ob.register_creddef(creddef)
    if resp:
        config.agent_data.creddef_id = resp["credential_definition_id"]
        config.agent_data.creddefs[schema_name] = resp["credential_definition_id"]
        logging.debug(f"Registered schema with id: %s, and creddef_id: %s", id, resp["credential_definition_id"])
        return id, resp["credential_definition_id"]

def get_schema_name(creddef):
    resp = ob.get_creddef(creddef)
    if not resp:
        return False

    schema_id = resp["credential_definition"]["schemaId"]
    resp = ob.get_schema(schema_id)

    if not resp:
        return False
    return resp["schema"]["name"]


#####VALIDATORS#####
def is_credential_stored(name):
    credentials = ob.get_credentials()
    res = credentials["results"]
    matching_creds = [x for x in res if name in x["schema_id"]]
    if not matching_creds:
        return False
    return True

def is_proof_validated(schema_name, proof_name=None, ex_id=None):
    proof_records = ob.get_pres_ex_records()
    results = proof_records["results"]
    if results:
        for result in results:
            if "verified" in result:
                if result["verified"] == "true":
                    attrs = result["presentation_request"]["requested_attributes"]
                    for attr in attrs:
                        for attrname in attrs[attr]:
                            if attrname == "restrictions":
                                restrictions = attrs[attr][attrname]
                                for restriction in restrictions:
                                    if "cred_def_id" in restriction:
                                        name = get_schema_name(restriction["cred_def_id"])
                                        if name == schema_name:
                                            return True
    return False

def get_proof_validated(schema_name, proof_name=None, ex_id=None):
    proof_records = ob.get_pres_ex_records()
    results = proof_records["results"]
    if results:
        for result in results:
            if "verified" in result:
                if result["verified"] == "true":
                    attrs = result["presentation_request"]["requested_attributes"]
                    for attr in attrs:
                        for attrname in attrs[attr]:
                            if attrname == "restrictions":
                                restrictions = attrs[attr][attrname]
                                for restriction in restrictions:
                                    if "cred_def_id" in restriction:
                                        name = get_schema_name(restriction["cred_def_id"])
                                        if name == schema_name:
                                            return True
    return False

def have_receieved_proof_proposal(schema_name=None):
    proof_records = ob.get_pres_ex_records()
    results = proof_records["results"]
    if results:
        for result in results:
            state = result["state"]
            if state == "proposal_received":
                proposal = result["presentation_proposal_dict"]["presentation_proposal"]
                attrs = proposal["attributes"]
                for attr in attrs:
                    if "cred_def_id" in attr:
                        if get_schema_name(attr["cred_def_id"]) == schema_name:
                            return True
    return False


#extract value from credential
def get_cred_attr_value(name, offer):
    attributes = offer["credential_proposal_dict"]["credential_proposal"]["attributes"]
    for attr in attributes:
        if attr["name"] == name:
            return attr["value"]
    return False


def get_cred_attrs(offer):
    return offer["credential_proposal_dict"]["credential_proposal"]["attributes"]


def gen_package_no(n=7):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(random.randint(range_start, range_end))

def gen_product_id(n=4):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(random.randint(range_start, range_end))

def gen_transaction_id(n=5):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return "t_id_" + str(random.randint(range_start, range_end))

def parse_payment_endpoint(data):
    get_cred_attr_value("", data)
