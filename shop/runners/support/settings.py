import os
import logging
import random


log = logging.getLogger(__name__)

DEMO_PRODUCT_ID = "asd123f"
DEMO_PACKAGE_NO = "123456"

class VendorData:
    def __init__(self):
        self.current_connection = None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.active = False
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.payment_creddef = None
        self.proofs = {}
        self.creddefs = {}
        self.transactions = []
        self.product_id = None
        self.package_no = None
        self.transaction_request = None

        self.stages = [
            "start",
            "purchase_requested",
            "purchase_approved",
            "payment_proven",
            "package_shipped",
            "receipt_confirmed",
            "completed"
        ]
        self.stage = 0


    def get_stage(self):
        return self.stages[self.stage]

    def incoming_transaction(self, product_id):
        log.debug("Vendor at stage: %s", self.get_stage())
        if self.stage == 0:
            self.stage += 1

    def approved_transaction(self, product_id):
        if self.stage == 1:
            self.stage += 1
            log.debug("Vendor at stage: %s", self.get_stage())

    def payment_proven(self):
        if self.stage == 2:
            self.stage += 1
            log.debug("Vendor at stage: %s", self.get_stage())

    def package_shipped(self):
        if self.stage == 3:
            self.stage += 1
            log.debug("Vendor at stage: %s", self.get_stage())

    def receipt_confirmed(self, package_no=None):
        if self.stage == 4:
            self.stage += 1
            log.debug("Vendor at stage: %s", self.get_stage())
            log.debug("======UV: Receipt Credential Received for package: %s", )
#
    def receipt_proven(self, package_no):
        if self.stage == 5:
            self.stage += 1
            log.debug("Vendor at stage: %s", self.get_stage())
#
    def get_transactions(self):
        results = {}
        for transaction in self.transactions:
            if transaction["stage"] in results:
                results[transaction["stage"]] = results[transaction["stage"]] = 1
            else:
                results[transaction["stage"]] = 1
        return results

class UserData:
    def __init__(self):
        self.current_connection = None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.active = False
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.payment_creddef = None
        self.proofs = {}
        self.creddefs = {}
        self.transactions = []
        self.stages = [
            "start",
            "agreement_proposed",
            "agreement_received",
            "payment_agreement_proven",
            "payment_credential_received",
            "payment_credential_proven",
            "package_credential_received",
            "package_receipt_validated",
            "completed"
        ]
        self.stage = 0
        self.product_id = None
        self.package_no = None
        self.payment_agreement = None

    def get_stage(self):
        return self.stages[self.stage]

    def requested_payment_agreement(self):
        log.debug("0 called, with stage value: %s and get val: %s", self.stage, self.get_stage())
        if self.stage == 0:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def received_agreement_cred(self):
        log.debug("1 called")
        if self.stage == 1:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def payment_agreement_proven(self, product_id, package_no=None):
        log.debug("2 called")
        if self.stage == 2:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def payment_credential_received(self):
        log.debug("3 called")
        if self.stage == 3:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def payment_credential_proven(self, package_no):
        log.debug("4 called")
        if self.stage == 4:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def package_credential_received(self):
        log.debug("5 called")
        if self.stage == 5:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def package_receipt_validated(self, package_no):
        log.debug("6 called")
        if self.stage == 6:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())

    def package_ownership_proven(self, package_no):
        log.debug("7 called")
        if self.stage == 7:
            self.stage += 1
            log.debug("User at stage: %s", self.get_stage())
            log.debug("UV: Receipt Credential Received for package number: %s", package_no)


class BankData:
    def __init__(self):
        self.current_connection = None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.active = False
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.payment_creddef = None
        self.proofs = {}
        self.creddefs = {}
        self.transactions = []
        self.stages = [
            "start",
            "payment_agreement_validated",
            "completed"
        ]

        self.stage = 0
        self.product_id = None

    def get_stage(self):
        return self.stages[self.stage]

    def validate_agreement(self):
        if self.stage == 0:
            self.stage += 1
            log.debug("Bank at stage: %s", self.get_stage())

        elif self.stage == 2:
            self.stage = 1

    def issued_payment_credential(self):
        if self.stage == 1:
            self.stage += 1
            log.debug("Bank at stage: %s", self.get_stage())

class ShipperData:
    def __init__(self):
        self.current_connection=None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.active = False
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.payment_creddef = None
        self.proofs = {}
        self.creddefs = {}
        self.stages = [
            "start",
            "package_received",
            "receipt_issued",
            "completed"
        ]
        self.stage = 0
        self.package_no = None

    def get_stage(self):
        return self.stages[self.stage]

    def package_received(self):
        if self.stage == 0:
            self.stage += 1
            log.debug("Shipper stage: %s", self.get_stage())
        elif self.stage == 2:
            self.stage = 1

    def ownership_validated(self):
        if self.stage == 1:
            self.stage += 1
            log.debug("Shipper stage: %s", self.get_stage())

def gen_package_no(n=7):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(random.randint(range_start, range_end))


def setup():
    global agent_data
    global role
    role = os.getenv("ROLE")

    if role == "flaskvendor":
        agent_data = VendorData()

    elif role == "flaskuser":
        agent_data = UserData()

    elif role == "flaskshipper":
        agent_data = ShipperData()

    elif role == "flaskbank":
        agent_data = BankData()


agent_data = None
role = None





