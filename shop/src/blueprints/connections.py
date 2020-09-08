from flask import Flask, Blueprint, render_template, make_response, redirect, request
import json
import logging
import urllib
import base64
import os
import sys
# blueprint for handling requests from the connections tab / related
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.support.outbound_routing as ob
import src.support.settings as config

connections = Blueprint('connections', __name__)

@connections.route("/connections/create_invite/", methods=["GET"])
def make_inv():
    resp = ob.create_invite()
    return make_response(json.dumps(resp["invitation"]), 200)

@connections.route("/connections/current/", methods=["POST"])
def set_current_conn():
    data = request.json
    if "selected_connection" in data:
        if data["selected_connection"] is not None:
            config.agent_data.current_connection = data["selected_connection"]
    return redirect(request.referrer)


@connections.route("/connections/receive_invite/", methods=["POST"])
def rec_inv():
    invdict = request.form.to_dict()
    invite = invdict['invite']

    if invite.startswith("http"):
        parsed_url = urllib.parse.urlparse(invite)
        query_string = parsed_url.query
        query_string = query_string[4:]
        invite = base64.b64decode(query_string)
        invite = invite.decode("utf-8")

    ob.receive_invite(invite)
    return redirect(request.referrer)

@connections.route("/connections/get_connections/", methods=["GET"])
def get_conns():
    r = make_response(json.dumps(ob.get_connections()))
    r.mimetype ="application/json"
    return r

@connections.route("/connections/get_active_connections/", methods=["GET"])
def get_active_conns():
    cons = ob.get_connections()

    agents = [
        (x['their_label'], x['connection_id']) for x in cons['results'] if x['state'] == "active"
    ]

    if not config.agent_data.current_connection:
        current = "None"
    else:
        current = config.agent_data.current_connection

    conn_details = ob.get_connection_details(current)

    if not conn_details:
        return make_response({"result": "no active connections"})

    if "their_label" in conn_details:
        their_label = conn_details['their_label']
        agents.append(("current_connection", their_label))

    if not agents:
        return make_response(json.dumps({"result": "no active connections"}), 200)

    r = make_response(json.dumps({x[0]: x[1] for x in agents}), 200)
    r.mimetype = "application/json"
    return r
