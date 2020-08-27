import subprocess
import os
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        "--endpoint", endpoint,
        "--label", label,
        "--inbound-transport", "http", "0.0.0.0", str(start_port),
        "--outbound-transport", "http",
        "--admin", "0.0.0.0", str(start_port + 1),
        "--admin-insecure-mode",
        "--wallet-type", "indy",
        "--wallet-name", "flask.wallet",
        "--wallet-key", "flask.wallet.key",
        "--preserve-exchange-records",
        "--auto-ping-connection",
        "--auto-respond-messages",
        "--auto-accept-requests",
        "--auto-accept-invites",
        "--auto-store-credential",
        "--debug-connections",
        "--debug-credentials",
        "--debug-presentations",
        "--genesis-url", genesis_url,
        "--seed", seed,
        "--preserve-exchange-records",
        "--webhook-url", webhook_url
    ]

    if os.getenv("ROLE") == "user":
        args.append("--wallet-local-did")

    runcmds = ["python3", "./bin/aca-py", "start"]
    args = runcmds + args
    print("starting with args", args)
    myenv = os.environ.copy()
    subprocess.Popen(args, env=myenv, encoding="utf-8")

