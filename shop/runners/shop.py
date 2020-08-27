from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

# Routes for the shop tab

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

shop = Blueprint('shop', __name__)

@shop.route("/home/shop", methods=["GET"])
def render_shop_actions():
    stage = config.agent_data.get_stage()
    if config.agent_data.has_public:
        did = get_public_did()
        return render_template('shop.html', name=config.role.capitalize(), stage=stage, did=did)
    else:
        return render_template('shop.html', name=config.role.capitalize(), stage=stage)


def get_public_did():
    resp = ob.get_public_did()
    res = resp["result"]
    if "did" in res:
        return res["did"]
    else:
        return None
