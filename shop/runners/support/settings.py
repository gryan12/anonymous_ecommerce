
class Data:
    def __init__(self):
        self.current_connection =None,
        self.previews = {}
        self.creddef_id = None
        self.attrs = {}
        self.connections = []
        self.active = False
        self.has_public = False
        self.stage = 0
        self.agent_role = None
        self.test = "hello"

        self.bank_did = None
        self.shipper_did = None
        self.vendor_did = None

        self.presex_roles = {} #dict (placeholder cache) of <pres_ex_id> : <role>
        self.credex = {} #dict (placeholder cache) of <cred_ex_id> : <role>

    def add_connection(self, conn_id):
        self.connections.append(conn_id)
        self.current_connection = conn_id,

    def add_preview(self, creddef_id, preview):
        self.previews[creddef_id] = preview

    def add_attrs(self, creddef_id, attrs):
        self.attrs[creddef_id] = attrs

def setup():
    global agent_data
    agent_data = Data()
    agent_data.test = "Hello this is a test variable from settings"


agent_data = None

testvar = "hello"




