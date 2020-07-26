import unittest
import sys
import os

from ..runners.support.creds import build_proof_request, build_cred, build_schema, buildProofWebRequest, build_cred_definition

class TestCredMethods(unittest.TestCase):

    def build_cred_returns_dict(self):
        builder = build_cred()
        cred = builder.build()
        self.assertTrue(cred)
        self.assertTrue(isinstance(cred, dict))

    def build_proof_reqest_returns_dict(self):
        builder = build_proof_request("test", "2")
        proof_req = builder.build()
        self.assertTrue(isinstance(proof_req, dict))

