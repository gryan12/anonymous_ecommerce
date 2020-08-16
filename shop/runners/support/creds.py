import json

# Code for the creation of aries JSON objects
# needed for aries protocols

#TYPES = {
#    "propose_presentation": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/propose-presentation",
#    "presentation_preview":
#}


def build_schema(name, version, attributes):
    schema = {
        "schema_name": name,
        "schema_version": version,
        "attributes": attributes
    }
    return schema

def build_cred_definition(schema_id, revocation=False):
    definition = {
        "schema_id": schema_id,
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
        self.conn_id = None
        self.issuer_did = None
        self.schema_name = None

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
            "@type":"did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": [{"name": n, "value": v} for (n,v) in self.attributes.items()]
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


def build_credential_proposal(
                   connection_id,
                   comment="",
                   prop_schema=None,
                   schema_name=None,
                   schema_version=None,
                   cred_def_id = None,
                   issuer_did=None
                   ):

    proposal = {
        "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.1/propose-credential",
        "comment": comment,
        "connection_id": connection_id,
    }

    if schema_version:
        proposal["schema_version"] = schema_version
    if cred_def_id:
        proposal["cred_def_id"] = cred_def_id
    if issuer_did:
        proposal["issuer_did"] = issuer_did
    if schema_name:
        proposal["schema_name"] = schema_name
    if prop_schema:
        proposal["credential_proposal"] = prop_schema

    return proposal


###PROOF BUILDERS###

def build_proof_request(name=None, version=None):
    return ProofReqBuilder(name=name, version=version)

def build_proof_proposal(comment="Proposal of proof"):
    return ProofReqBuilder()

class ProofReqBuilder:
    def __init__(self, name=None, version= None):
        self.attributes = []
        self.preds = []
        self.name = name
        self.version = version
        self.as_json = False
        self.tracing = False
        self.comment = None

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


    #todo make cleaner, include optional fields
    def build_proposition(self):
        presentation_preview = {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/presentation-preview",
            "attributes": self.attributes,
            "predicates": self.preds,
        }
        proof_proposition = {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/propose-presentation",
            "comment": self.comment,
            "presentation_proposal": presentation_preview
        }

        return proof_proposition


def build_proof_proposal(name=None):
    return ProofPropositionBuilder()



class ProofPropositionBuilder:

    def __init__(self, name=None):
        self.name = name
        self.attrs = []
        self.preds = []
        self.type = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/propose-presentation"


    def withAttribute(self, name, cred_def_id=None, mime_type=None, value=None, referent=None):
        attribute = {
            "name": name,
        }
        if cred_def_id:
            attribute["cred_def_id"] = cred_def_id

        if value:
            attribute["value"] = value

        if cred_def_id and referent:
            attribute["referent"] = referent

        self.attrs.append(attribute)
        return self

    def withPredicate(self, name, threshold, cred_def_id=None, predicate=">="):

        predicate = {
            "name": name,
            "cred_def_id": cred_def_id,
            "predicate": predicate,
            "threshold": threshold
        }

        self.preds.append(predicate)
        return self


    def build(self, connection_id, comment=None, auto_present=True):

        preview = {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/presentation-preview",
            "attributes": self.attrs,
            "predicates": self.preds
        }
        proposition = {
            "@type": self.type,
            "connection_id": connection_id,
            "presentation_proposal": preview
        }
        if comment:
            proposition["comment"] = comment

        return proposition


def buildProofWebRequest(connection_id, proof, trace=False):
    webReq = {
        "connection_id": connection_id,
        "proof_request": proof,
        "trace": trace
    }
    return json.dumps(webReq)

def pretty_print_obj(json_dict):
    pretty = json.dumps(json_dict, indent=2)
    print(pretty)
    return pretty