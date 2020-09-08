from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

# blueprint for routes from the credentials page / related
import src.support.outbound_routing as ob
import src.support.settings as config
import src.transaction_logic as trans

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

    if role == "bank":
        logging.debug("MAJOR STAGE: ISSUING PAYMENT CRED")
        trans.send_payment_cred_offer(config.agent_data.current_connection, config.agent_data.creddef_id)

    elif role == "vendor":
        logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        trans.send_package_cred_offer(config.agent_data.current_connection, config.agent_data.creddefs["package_cred"])

    elif role == "shipper":
        logging.debug("MAJOR STAGE 4: ISSUEING PACKAGE CRED")
        trans.send_package_receipt_cred_offer(config.agent_data.current_connection, config.agent_data.creddef_id, config.agent_data.get_package_no())

    return make_response({"code":"success", "role": role}, 200)


@credentials.route("/credentials/propose/", methods=["GET"])
def prop_cred():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    ##propose payment credential
    if config.role == "user":
        logging.debug("proposing payment agreement credential")
        ##todo implement input through web

        if not config.agent_data.product_id:
            product_id = trans.gen_product_id()
        else:
            product_id = config.agent_data.product_id

        trans.send_payment_agreement_proposal(product_id)

        return make_response({"code": "received"})

    return make_response({"code": "failure", "reason": "Error in proposing agreement"})

@credentials.route("/credentials/shop/received_package/", methods=["GET"])
def received_package():

    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})
    if config.role != "shipper":
        make_response({"code": "not avialable for this agent"}, 500)

    creddef_id = config.agent_data.creddefs["received_package"]
    trans.send_package_receipt_cred_offer(config.agent_data.current_connection, creddef_id)

    return make_response({"code": "received"})

@credentials.route("/credentials/shop/request_purchase/", methods=["GET"])
def req_purchase():

    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})

    if config.role != "user":
        make_response({"code": "not avialable for this agent"}, 500)

    ##todo implement input through web
    product_id = trans.gen_product_id()
    trans.send_payment_agreement_proposal(product_id)
    return make_response({"code": "received"})


@credentials.route("/credentials/shop/approve_purchase/", methods=["GET"])
def approve_purchase():
    if not ob.hasActiveConnection():
        return make_response({"code": "failure", "reason": "no active connections"})
    if config.role != "vendor":
        make_response({"code": "not avialable for this agent"}, 400)
    trans.approve_payment_agreement()
    return make_response({"code": "received"})
