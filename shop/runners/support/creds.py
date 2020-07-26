import json


# just proving an api for making requests/proofs/creds more relaxing
# i'm sure that this c++ builder style-code is not very pythonesque
# so sry 4 tht will change

def build_schema(name, version, attributes):
    schema = {
        "schema_name": name,
        "schema_version": version,
        "attributes": attributes
    }
    return schema

def build_cred_definition(schema_id, revocation=False):
    definition = {
        "schema_id":schema_id,
        "support_revocation": revocation
    }
    return definition

def build_cred(creddef_id):
    return CredBuilder(creddef_id)

class CredBuilder:
    def __init__(self, creddef_id=None):
        self.attributes = {}
        self.as_json = False
        self.creddef_id = creddef_id
        self.type = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview"
        self.conn_id = None

    def withName(self, name):
        self.name = name
        return self

    def with_conn_id(self, conn_id):
        self.conn_id =conn_id
        return self

    def with_type(self, type):
        self.type = type
        return self

    def withId(self, id):
        self.creddef_id = id
        return self

    def withVersion(self, version):
        self.version = version
        return self

    def with_attribute(self, attribute):
        self.attributes.update(attribute)
        return self

    def with_attributes(self, attributes):
        if not self.attributes: 
            self.attributes = attributes
        else:
            self.attributes.update(attributes)
        return self

    def asJson(self):
        self.as_json = True
        return self

    def build_preview(self):
        preview = {
            "@type":self.type,
            "attributes": [{"name":n, "value":v} for (n,v) in self.attributes.items()]
        }
        return preview

    def build(self):
        credential = {
            "name":self.name,
            "version": self.version,
            "attributes": self.attributes
        }
        if self.as_json:
            return json.dumps(credential)
        return credential


    def build_offer(self, comment="", auto_remove=False, trace=False):
        req = {
           "connection_id" : self.conn_id,
           "cred_def_id": self.creddef_id,
           "comment": comment,
           "auto-remove": False,
           "credential_preview": self.build_preview(),
           "trace": False
        }
        return req


def build_proof_request(name=None, version=None):

    return ProofReqBuilder(name=name, version=version)

class ProofReqBuilder:
    def __init__(self, name=None, version= None):
        self.attributes = []
        self.preds = []
        self.name = name
        self.version = version
        self.as_json = False
        self.tracing = False

    def withName(self, name):
        self.name = name
        return self

    def withVersion(self, version):
        self.version = version
        return self

    ##takes completed attribute dict
    def withAttribute(self, attribute):
        self.attributes.append(attribute)
        return self

    #restrictions is a list of dicts e.g. [{"issuer_did":rand_di},{"creddef_id":rand_id}]
    def withAttribute(self, name, restrictions=None, revoked=None):
        att = {
            "name":name
        }

        if restrictions:
            att["restrictions"] = restrictions

        if revoked:
            att["non_revoked"] = revoked

        self.attributes.append(att)
        return self

    ##takes compelete pred dict
    def withPred(self, pred):
        self.preds.append(pred)
        return self

    ##currently only >= supported so.
    def withPred(self, name, restrictions, p_type = ">=", p_value = 0):

        pred = {
            "name": name,
            "p_type": p_type,
            "p_value": p_value,
            "restrictions":restrictions,
        }

        self.preds.append(pred)
        return self

    def withPreds(self, preds): 
        if not self.preds: 
            self.preds = preds
        else: 
            self.preds.extend(preds)
        return self

    ##takes list of attrs
    def withAttributes(self, attributes):
        self.attributes = attributes
        return self


    def with_conn_id(self, conn_id):
        self.conn_id = conn_id
        return self

    def with_tracing(self, tracing):
        self.tracing = tracing
        return self

    def build(self): 

        proof_request = {
            "name": self.name,
            "version": self.version,
            "requested_attributes": {
                f"0_{attr['name']}_uuid": attr for attr in self.attributes
            },
            "requested_predicates": {
                f"0_{pred['name']}_GE_uuid": pred for pred in self.preds
            }
        }

        web_req = {
            "connection_id": self.conn_id,
            "proof_request": proof_request,
            "trace": self.tracing
        }

        if self.as_json:
            return json.dumps(web_req)
        return web_req


def buildProofWebRequest(connection_id, proof, trace=False): 
    webReq =  {
        "connection_id":connection_id,
        "proof_request":proof,
        "trace": trace
    }
    return json.dumps(webReq)


