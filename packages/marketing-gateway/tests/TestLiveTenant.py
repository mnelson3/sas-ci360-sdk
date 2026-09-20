#! /usr/local/bin/python3
# -*- mode: python ; coding: utf-8 -*-

"""
UAT / integration tier for marketing-gateway (TRD 2.9): exercises the
client against a real CI360 tenant instead of a mocked one. Every test
here is skipped, not failed, unless CI360_HOST, CI360_SECRET_KEY, and
CI360_TENANT_ID are all set - so this file is always safe to collect,
including in the default CI job, where those variables are never set.

Run it deliberately with real credentials:
	export CI360_HOST="extapigwservice-<env>.ci360.sas.com"
	export CI360_SECRET_KEY="..."
	export CI360_TENANT_ID="..."
	pytest tests/TestLiveTenant.py -v

See the sas-ci360-sdk repository's UAT.md for the full runbook.

The only call here is get_root(), a read-only GET against the API's
top-level resource links.
"""

import os
import unittest

from sasci360apimarketinggateway import root

_HOST = os.environ.get("CI360_HOST")
_SECRET_KEY = os.environ.get("CI360_SECRET_KEY")
_TENANT_ID = os.environ.get("CI360_TENANT_ID")


@unittest.skipUnless(
	_HOST and _SECRET_KEY and _TENANT_ID,
	"CI360_HOST, CI360_SECRET_KEY, and CI360_TENANT_ID must all be set to run live-tenant tests",
)
class TestLiveTenant(unittest.TestCase):

	def setUp(self) -> None:
		# Root.get_root() builds its own https:// prefix, so this client
		# needs the bare hostname CI360_HOST is documented as - unlike the
		# sol-* clients' config, which needs the full URL.
		self.root = root.Root(
			algorithm="HS256",
			api="/marketingGateway",
			encoding="UTF-8",
			host=_HOST,
			secret_key=_SECRET_KEY,
			tenant_id=_TENANT_ID,
		)

	def test_get_root_returns_a_real_response(self):
		result = self.root.get_root()
		self.assertIsNotNone(result)


if __name__ == "__main__":
	unittest.main()
