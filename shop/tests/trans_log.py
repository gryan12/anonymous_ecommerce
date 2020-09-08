import unittest
import sys
import os

from ..src.support.creds import build_proof_request, build_cred, build_schema, buildProofWebRequest, build_cred_definition
from ..src.support.outbound_routing import post, get, get_status, create_invite,


#basic aries interaction tests
class TestOutboundFunctions(unittest.TestCase):

    def connected_to_aries(self):
        self.assertTrue(get_status)

    def get_returns_dict_on_success(self):
        self.assertTrue(isinstance(get_status(), dict))

    def post_returns_dict_on_success(self):
        self.assertTrue(isinstance(create_invite(), dict))

    def get_returns_none_on_failure(self):
        self.assertFalse(get("false_url"))


