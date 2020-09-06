import os
import logging
import random


log = logging.getLogger(__name__)

#globals
agent_data = None
role = None


DEMO_PRODUCT_ID = "asd123f"
DEMO_PACKAGE_NO = "123456"

# Code which holds state information for each agent.
# Separate class for each agent state.
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
        self.transaction_request = None

        self.product_id = None
        self.package_no = None
        self.amount = None
        self.transaction_id = None
        self.payment_endpoint = None


        # transactions tages
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


    ##transaction state functions
    def get_stage(self):
        return self.stages[self.stage]

    def get_endpoint(self):
        if not self.payment_endpoint:
            self.payment_endpoint = gen_endpoint_id()
        return self.payment_endpoint

    def update_product_id(self, product_id):
        log.debug("New message pertaining product of id: %s", product_id)
        self.product_id = product_id

    def update_package_no(self, package_no):
        log.debug("New message pertaining package of numner: %s", package_no)
        self.package_no = package_no

    def update_transaction_id(self, t_id):
        log.debug("New message pertaining transaction_id of id: %s", t_id)
        self.transaction_id = t_id

    def output_stage(self):
        log.debug("Vendor at stage: %s", self.get_stage())

    ##transaction functions
    def incoming_transaction(self, product_id):
        if self.stage == 0:
            self.stage += 1
            self.update_product_id(product_id)
            self.output_stage()

    def approved_transaction(self):
        if self.stage == 1:
            self.stage += 1
            self.output_stage()


    def payment_proven(self, transaction_id):
        if self.stage == 2:
            self.stage += 1
            self.output_stage()
            self.update_transaction_id(transaction_id)


    def package_shipped(self):
        if self.stage == 3:
            self.stage += 1
            self.output_stage()

    def receipt_confirmed(self, package_no=DEMO_PACKAGE_NO):
        if self.stage == 4:
            self.stage += 1
            self.update_package_no(package_no)
            self.output_stage()
            log.debug("receipt confirmed for package: %s", package_no)
#
    def receipt_proven(self, package_no=None):
        if self.stage == 5:
            self.stage += 1
            self.output_stage()
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
        self.stage = 0
        self.FICTIONAL_ADDRESS = "11, My Fictional Street, QWERTY"

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

        self.product_id = None
        self.amount = 0
        self.transaction_id = None
        self.payment_endpoint = None
        self.package_no = None

    def get_stage(self):
        return self.stages[self.stage]

    def get_transaction_values(self):
        ansdict = {
            "product_id": self.product_id or "none",
            "amount": self.amount or "none",
            "transaction_id": self.amount or "none",
            "payment_endpoint": self.payment_endpoint or "none",
            "package_no": self.package_no or "none"
        }
        return ansdict

    def update_product_id(self, product_id):
        log.debug("New message pertaining product of id: %s", product_id)
        self.product_id = product_id

    def update_amount(self, amount):
        log.debug("New message pertaining amount owed of: %s", amount)
        self.amount = amount

    def update_package_no(self, package_no):
        log.debug("New message pertaining package of number: %s", package_no)
        self.package_no = package_no

    def update_transaction_id(self, t_id):
        log.debug("New message pertaining transaction_id of id: %s", t_id)
        self.transaction_id = t_id

    def update_payment_endpoint(self, endpoint):
        log.debug("New message pertaining payment_endpoint: %s", endpoint)
        self.payment_endpoint = endpoint

    def output_stage(self):
        log.debug("User at stage: %s", self.get_stage())

    def requested_payment_agreement(self):
        log.debug("0 called, with stage value: %s and get val: %s", self.stage, self.get_stage())
        if self.stage == 0:
            self.stage += 1
            self.output_stage()

    def received_agreement_cred(self, amount, endpoint):
        if self.stage == 1:
            self.stage += 1
            self.update_payment_endpoint(endpoint)
            self.update_amount(amount)
            self.output_stage()

    def payment_agreement_proven(self):
        if self.stage == 2:
            self.stage += 1
            self.output_stage()

    def payment_credential_received(self, transaction_id):
        if self.stage == 3:
            self.stage += 1
            self.output_stage()
            self.update_transaction_id(transaction_id)

    def payment_credential_proven(self):
        if self.stage == 4:
            self.stage += 1
            self.output_stage()

    def package_credential_received(self, package_no):
        if self.stage == 5:
            self.stage += 1
            self.output_stage()
            self.update_package_no(package_no)

    def package_receipt_validated(self, package_no):
        if self.stage == 6:
            self.stage += 1
            self.output_stage()
            self.update_package_no(package_no)

    def package_ownership_proven(self, package_no=None):
        if self.stage == 7:
            self.stage += 1
            self.output_stage()
            package_no = package_no or self.package_no
            log.debug("Receipt Credential Received for package number: %s", package_no)


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
        self.payment_endpoint = None

    def get_stage(self):
        return self.stages[self.stage]

    def validate_agreement(self, endpoint):
        if self.stage == 0:
            self.stage += 1
            self.payment_endpoint = endpoint
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
            "receipt_issued",
            "completed"
        ]
        self.stage = 0

        self.package_no = None

    def update_package_no(self, package_no):
        log.debug("New message pertaining package of numner: %s", package_no)
        self.package_no = package_no

    def get_package_no(self):
        if self.package_no:
            return self.package_no
        else:
            log.debug("no package no set")
            return DEMO_PACKAGE_NO


    def output_stage(self):
        log.debug("Shipper stage: %s", self.get_stage())

    def get_stage(self):
        return self.stages[self.stage]

    def receipt_issued(self, package_no=None):
        if self.stage == 0 and self.package_no:
            self.stage += 1
            self.output_stage()
        else:
            if not self.package_no:
                log.debug("Error: no package number detected")

    def ownership_validated(self, package_no):
        if self.stage == 1:
            self.stage += 1
            self.output_stage()
            log.debug("Package ownership validated for package number: %s. Sending package :)", package_no)

def gen_package_no(n=7):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(random.randint(range_start, range_end))

def gen_transaction_id(n=5):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return "t_id_" + str(random.randint(range_start, range_end))


def get_transaction_values():
    values = ["package_no", "payment_endpoint", "amount", "transaction_no", "product_id"]
    resp = {}
    for value in values:
        val = getattr(agent_data, value, False)
        if val:
            resp[value] = val
    return resp

# init data
def setup():
    global agent_data
    global role
    role = os.getenv("ROLE")

    if role == "vendor":
        agent_data = VendorData()

    elif role == "user":
        agent_data = UserData()

    elif role == "shipper":
        agent_data = ShipperData()

    elif role == "bank":
        agent_data = BankData()


def gen_endpoint_id(n=4):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return "z_" + str(random.randint(range_start, range_end))




