import subprocess
import os
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runners.support.settings as config

#def aries_init():
#    config.setup()
#    start_port = int(os.getenv("AGENT_PORT"))
#    agent_role = os.getenv("ROLE")
#    config.agent_data.agent_role = agent_role
#    host = os.getenv("DOCKERHOST")
#    logging.debug("Init controller with role: %s, listenting on port: %s", agent_role, str(start_port))
#
#    if not start_port:
#        logging.debug("error: no assigned port")
#        sys.exit(-1)
#
#    ##init aries
#    name, seed = gen_rand_seed()
#
#    if agent_role is not "flaskuser":               ##the user should not be on the public ledger
#        register_did("http://" + host + ":9000", seed, agent_role)
#
#    agent_url = "http://" + host + ":" + str(start_port + 1)
#    logging.debug("Agent url: %s", agent_url)
#    ob.set_agent_url(agent_url)
#
#    start_aries(start_port, seed, agent_role)
#

def flatten(args):
    for arg in args:
        if isinstance(arg, (list, tuple)):
            yield from flatten(arg)
        else:
            yield arg


def start_aries(start_port, seed, label, genesis_url=None):
    ledger_url = os.getenv("LEDGER_URL")

    if not ledger_url:
        ledger_url = "http://172.17.0.1:9000"

    if not genesis_url:
        genesis_url = ledger_url + "/genesis"

    host = os.getenv("DOCKERHOST")
    endpoint = "http://" + host + ":" + str(start_port)
    webhook_url = "http://" + "0.0.0.0" + ":" + str(start_port + 2) + "/webhooks"

    args = [
        ("--endpoint", endpoint),
        ("--label", label),
        ("--inbound-transport", "http", "0.0.0.0", str(start_port)),
        ("--outbound-transport", "http"),
        ("--admin", "0.0.0.0", str(start_port + 1)),
        "--admin-insecure-mode",
        ("--wallet-type", "indy"),
        ("--wallet-name", "flask.wallet"),
        ("--wallet-key", "flask.wallet.key"),
        "--preserve-exchange-records",
        "--auto-ping-connection",
        "--auto-respond-messages",
        "--auto-accept-requests",
        "--auto-accept-invites",
        "--auto-store-credential",
        ("--genesis-url", genesis_url),
        ("--seed", seed),
        ("--webhook-url", webhook_url)
    ]

    args = list(flatten((["python3", "./bin/aca-py", "start"], args)))
    print("starting with args", args)
    myenv = os.environ.copy()
    subprocess.Popen(args, env=myenv, encoding="utf-8")

#def register_did(ledger_url, seed=None, alias=None, role="TRUST_ANCHOR"):
#    content = {
#        "seed": seed,
#        "alias": alias,
#        "role": role,
#    }
#    response = requests.post(ledger_url + "/register", data=json.dumps(content))
#    return json.loads(response.text)
#
#def gen_rand_seed():
#    name = str(random.randint(100_000, 999_999))
#    seed = ("flask_s_000000000000000000000000" + name)[-32:]
#    return name, seed
#