import os

# obj to hold connection/cred/proof params in memory
class Data:
    def __init__(self):
        self.current_connection =None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.bank_did = None
        self.shipper_did = None
        self.vendor_did = None
        ##dict of schema names to their creddef ids
        self.creddefs = {}
        self.demo_stage = None
        self.demo_stages = {
            "flaskbank": [
                "start", "payment_agreement_approved", "payment_credential_issued"
            ],
            "flaskshipper": [
                "start", "package_received", "package_sent"
            ],
            "flaskuser": [
                "start",
                "proposed_purchase_credential",
                "purchase_agreement_credential_stored",
                "payment_credential_stored",
                "payment_credential_proved",
                "package_credential_stored",
                "package_crdential_proved"
            ],
            "flaskvendor": [
                "start",
                "purchase_credential_proposal_received",
                "issued_purchase_credential",
                "payment_credential_verified",
                "package_credential_issued",
                "receipt_credential_stored",
                "receipt_credential_proved",
            ]
        }

    def stage_completed(self):
        self.demo_stage = self.demo_stage + 1

    def get_stage(self):
        return self.demo_stages[self.agent_role][self.demo_stage]

    def finished(self):
        return self.demo_stage >= len(self.demo_stages[self.agent_role])


def setup():
    global agent_data
    global role
    role = os.getenv("ROLE")
    agent_data = Data()


agent_data = None
role = None





