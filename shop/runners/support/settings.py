import os

# obj to hold connection/cred/proof params in memory
class Data:
    def __init__(self):
        self.current_connection =None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.connections = []
        self.active = False
        self.has_public = False
        self.agent_role = None
        self.credentials = []
        self.bank_did = None
        self.shipper_did = None
        self.vendor_did = None
        ##dict of schema names to their creddef ids
        self.creddefs = {}

def setup():
    global agent_data
    global role
    role = os.getenv("ROLE")
    agent_data = Data()


agent_data = None
role = None





