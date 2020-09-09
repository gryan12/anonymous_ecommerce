import unittest
import sys
import os

from ..src.support.creds import build_proof_request, build_cred, build_schema, buildProofWebRequest, build_cred_definition
import src.support.settings as config

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


class TestConfig(unittest.TestCase):
    def agent_data_init_on_start(self):
        self.assertTrue(config.agent_data)

    def agent_has_role(self):
        self.assertTrue(config.role)

    def role_matches_data_structure(self):
        if config.role == "user":
            self.assertTrue(isinstance(config.agent_data, config.UserData))
        elif config.role == "vendor":
            self.assertTrue(isinstance(config.agent_data, config.VendorData))
        elif config.role == "shipper":
            self.assertTrue(isinstance(config.agent_data, config.ShipperData))
        elif config.role == "bank":
            self.assertTrue(isinstance(config.agent_data, config.BankData))

