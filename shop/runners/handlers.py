#### START interface routes
from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys


# not currently used

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

webhooks = Blueprint('webhooks', __name__)

log = logging.getLogger(__name__)


def handle_proposal_received():
    return True

def handle_presentation_received():
    return True

def handle_presentation_sent():
    return True

def request_received(data):
    pres_req = data["presentation_request"]
    presex_id = data["presentation_exchange_id"]
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


def verified(data):
    log.debug("Verified")
    if config.role == "vendor":
        if data["verified"] == "true":
            log.debug("payment proven")
            config.agent_data.payment_proven(config.DEMO_PRODUCT_ID)

    elif config.role == "user":
        if data["verified"] == "true":
            log.debug("Receipt proven")
            config.agent_data.package_receipt_validated(config.DEMO_PRODUCT_ID)

    elif config.role == "bank":
        if data["verified"] == "true":
            log.debug("Receipt proven")
            config.agent_data.validate_agreement()

    elif config.role == "shipper":
        if data["verified"] == "true":
            log.debug("Receipt proven")
            config.agent_data.ownership_validated()

