from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

proofs = Blueprint('proofs', __name__)

# This file contains the blueprint for proof-related interface requests

@proofs.route("/proofs/history", methods=["GET"])
def get_proof_history():
    return make_response(
        json.dumps(ob.get_pres_ex_records()),
        200
    )

@proofs.route("/proofs/request_proof/", methods=["GET"])
def req_proof():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("Has active connection :)")
    role= os.getenv("ROLE")

    if role == "vendor":
        trans.request_proof_of_payment()

    elif role == "shipper":
        trans.request_proof_of_ownership()

    return make_response({"code": "success"})

@proofs.route("/proofs/request", methods=["GET"])
def issue_proof_req():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("Has active connection :)")
    role=os.getenv("ROLE")
    if role == "vendor":
        trans.request_proof_of_payment()

    elif role == "shipper":
        trans.request_proof_of_ownership()

    return make_response({"code":"success"})


@proofs.route("/proofs/payment/propose_proof/", methods=["GET"])
def prop_proof():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose proof of payment
    if config.role == "user":
        logging.debug("proposing proof of payment")
        payment_creddef = trans.get_payment_creddefid()
        if not payment_creddef:
            return make_response({"code": "Do not have correct credential"})

        trans.propose_proof_of_payment(config.agent_data.current_connection, payment_creddef)

        return make_response({"code": "received"})
    else:
        return make_response({"code": "failed"}, 400)


@proofs.route("/proofs/shop/dispatch/", methods=["GET"])
def ready_for_dispatch():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose proof of payment
    if config.role != "vendor":
        return make_response({"code": "action unavailable for this demo agent"}, 500)

    logging.debug("proposing proof of package status")
    dispatch_creddef = trans.get_creddefid("received_package")
    if not dispatch_creddef:
        return make_response({"code": "Do not have correct credential"})

    trans.propose_proof_of_dispatch(config.agent_data.current_connection, dispatch_creddef)

    return make_response({"code": "received"})


@proofs.route("/proofs/payment/propose_proof/agreement", methods=["GET"])
def prop_agree_proof():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("proposing proof of purchase agreement")
    agreement_creddef = trans.get_creddefid("payment_agreement")
    trans.propose_proof_of_payment_agreement(config.agent_data.current_connection, agreement_creddef)
    return make_response({"code": "received"})


@proofs.route("/proofs/shop/dispatch/propose_proof/ownership", methods=["GET"])
def prop_prove_ownership():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    logging.debug("proposing proof of package ownership")
    ownership_creddef = trans.get_creddefid("package_cred")
    trans.propose_proof_of_ownership(config.agent_data.current_connection, ownership_creddef)
    return make_response({"code": "received"})


