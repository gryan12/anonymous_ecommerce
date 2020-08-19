from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

credentials = Blueprint('credentials', __name__)

@credentials.route("/credentials", methods=["GET"])
def get_creds():
    return make_response(
        json.dumps(ob.get_credentials()),
        200
    )
@credentials.route("/credentials/history", methods=["GET"])
def get_cred_ex_history():
    return make_response(
        json.dumps(ob.get_cred_ex_records()),
        200
    )

@credentials.route("/credentials/issue_cred/", methods=["GET"])
def issue_credreq():

    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "agent has no active connections"})

    role = os.getenv("ROLE")

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
@credentials.route("/credentials/propose/", methods=["GET"])
def prop_cred():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose payment credential
    if config.role == "flaskuser":
        logging.debug("proposing payment agreement credential")
        payment_creddef = trans.send_payment_agreement_proposal()

    return make_response({"code": "received"})


@credentials.route("/credentials/shop/received_package/", methods=["GET"])
def received_package():

    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})
    if config.role != "flaskshipper":
        make_response({"code": "not avialable for this agent"}, 500)

    creddef_id = config.agent_data.creddefs["received_package"]
    trans.send_package_receipt_cred_offer(config.agent_data.current_connection, creddef_id)

    return make_response({"code": "received"})

@credentials.route("/credentials/shop/request_purchase/", methods=["GET"])
def req_purchase():

    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    if config.role != "flaskuser":
        make_response({"code": "not avialable for this agent"}, 500)
    trans.send_payment_agreement_proposal()
    return make_response({"code": "received"})


@credentials.route("/credentials/shop/approve_purchase/", methods=["GET"])
def approve_purchase():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})
    if config.role != "flaskvendor":
        make_response({"code": "not avialable for this agent"}, 400)
    trans.approve_payment_agreement()
    return make_response({"code": "received"})
