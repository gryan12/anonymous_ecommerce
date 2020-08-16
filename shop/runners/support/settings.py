import os
import logging
import random


log = logging.getLogger(__name__)

DEMO_PRODUCT_ID = "asd123f"
DEMO_PACKAGE_NO = "123456"

class Data:
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
        self.demo_stage = 0

        self.transactions = [
            {"stage": "awaiting"}
        ]
        self.user_transactions = []



    def stage_completed(self):
        self.demo_stage = self.demo_stage + 1

    def get_stage(self):
        return self.demo_stages[self.agent_role][self.demo_stage]

    def finished(self):
        return self.demo_stage >= len(self.demo_stages[self.agent_role])

    def incoming_transaction(self, product_id):
        self.transactions.append(
            {"stage": "payment_requested",
            "product_id": product_id},
        )

    def approved_transaction(self, product_id):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_requested":
                if transaction["product_id"] == product_id:
                    transaction["stage"] = "payment_agreed"

    def payment_proven(self, product_id, package_no=None):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_agreed":
                if transaction["product_id"] == product_id:
                    transaction["stage"] = "payment_made"
                    transaction["package_no"] = package_no

    def package_shipped(self, package_no):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_made":
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = "package_shipped"

    def receipt_confirmed(self, package_no):
        for transaction in self.transactions:
            if "package_no" in transaction:
                if transaction["package_no"] == package_no:
                    transaction["status"] = "at_shipper"

    def receipt_proven(self, package_no):
            for transaction in self.transactions:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = "complete"

    def cred_issued(self, package_no):
        for transaction in self.transactions:
            if "package_no" in transaction:
                self.transactions.remove(transaction)


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

    def create_package_number(self):
        return random.randint(10, 12)

    def incoming_transaction(self, product_id):
        log.debug("=====Vendor: Agreement proposal for product: %s", product_id)
        self.transactions.append(
            {"stage": "payment_requested",
             "product_id": product_id},
        )

    def approved_transaction(self, product_id):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_requested":
                if transaction["product_id"] == product_id:
                    log.debug("Vendor: Agreement Credential Issued for package number: %s", product_id)
                    transaction["stage"] = "payment_agreed"

    def payment_proven(self, product_id):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_agreed":
                if transaction["product_id"] == product_id:
                    transaction["stage"] = "payment_made"
                    log.debug("====Vendor: Proof of payment sent product: %s", product_id)
                    #transaction["package_no"] = package_no

    def package_shipped(self, product_id, package_no):
        for transaction in self.transactions:
            if transaction["stage"] == "payment_made":
                if "product_id" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = "package_shipped"
                        log.debug("====Vendor: Package Shipped with package number: %s", package_no)

    def receipt_confirmed(self, package_no=None):
        log.debug("======UV: Receipt Credential Received for package: %s", )
        for transaction in self.transactions:
            if "package_no" in transaction:
                if transaction["package_no"] == package_no:
                    transaction["status"] = "at_shipper"
                    log.debug("====Vendor: Package Shipped with package number: %s", package_no)

    def receipt_proven(self, package_no):
        for transaction in self.transactions:
            if "package_no" in transaction:
                if transaction["package_no"] == package_no:
                    transaction["status"] = "complete"
                    log.debug("Vendor: Package status proof presentation sent to user: %s", package_no)

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
        print("INITTING USERDATA")
        self.current_connection = None,
        self.active = False
        self.connections = []
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.payment_creddef = None
        self.creddefs = {}
        self.transactions = []

        self.stages = [
            "agreement_proposed",
            "agreement_received",
            "payment_agreement_proven",
            "payment_credential_received",
            "payment_credential_proven",
            "package_receipt_validated",
            "package_ownership_proven",
            "completed"
        ]

    def requested_payment_agreement(self, product_id):
        log.debug("UU: Requested proposal for product: %s", product_id)
        self.transactions.append(
            {"stage": self.stages[0],
             "product_id": product_id},
        )

    def received_agreement_cred(self, product_id):
        log.debug("UV: Agreement Credential Received for package number: %s", product_id)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[0]:
                if transaction["product_id"] == product_id:
                    transaction["stage"] = self.stages[1]

    def payment_agreement_proven(self, product_id, package_no=None):
        log.debug("UV: Payment agreement proved to bank: %s", product_id)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[1]:
                if transaction["product_id"] == product_id:
                    transaction["stage"] = self.stages[2]
                    transaction["package_no"] = package_no

    def payment_credential_received(self, package_no):
        log.debug("UV: Receipt Credential Received for package number: %s", package_no)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[2]:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = self.stages[3]

    def payment_credential_proven(self, package_no):
        log.debug("UV: Receipt Credential Received for package number: %s", package_no)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[3]:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = self.stages[4]

    def package_credential_received(self, package_no):
        log.debug("UV: Receipt Credential Received for package number: %s", package_no)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[4]:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = self.stages[5]

    def package_receipt_validated(self, package_no):
        log.debug("UV: Receipt Credential Received for package number: %s", package_no)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[5]:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = self.stages[6]

    def package_ownership_proven(self, package_no):
        log.debug("UV: Receipt Credential Received for package number: %s", package_no)
        for transaction in self.transactions:
            if transaction["stage"] == self.stages[6]:
                if "package_no" in transaction:
                    if transaction["package_no"] == package_no:
                        transaction["status"] = self.stages[7]


def setup():
    global agent_data
    global role
    role = os.getenv("ROLE")

    agent_data = Data()

    if role == "flaskvendor":
        agent_data = VendorData()
    elif role == "flaskuser":
        agent_data = UserData()


agent_data = None
role = None





