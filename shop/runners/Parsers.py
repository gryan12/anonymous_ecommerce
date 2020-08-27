
class UserTransaction:
    def __init__(self):
        self.product_id = None
        self.amount = None
        self.package_no = None
        self.transaction_id = None
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

