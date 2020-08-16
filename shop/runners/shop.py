from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.outbound_routing as ob
import runners.support.settings as config
import runners.transaction_logic as trans

credentials = Blueprint('shop', __name__)


@credentials.route("/shop", methods=["GET"])
def render_shop_actions():
    return render_template('shop.html')

@credentials.route("/shop", methods=["GET"])
def get_cred_ex_history():
    return make_response(
        json.dumps(ob.get_cred_ex_records()),
        200
    )



