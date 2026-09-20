#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAT / integration tier for sol-execute (TRD 2.9): exercises the client
against a real CI360 tenant instead of a mocked one. Every test here is
skipped, not failed, unless CI360_HOST, CI360_SECRET_KEY, and
CI360_TENANT_ID are all set - so this file is always safe to collect,
including in the default CI job, where those variables are never set.

Run it deliberately with real credentials:
    export CI360_HOST="extapigwservice-<env>.ci360.sas.com"
    export CI360_SECRET_KEY="..."
    export CI360_TENANT_ID="..."
    pytest tests/test_live_tenant.py -v

See the sas-ci360-sdk repository's UAT.md for the full runbook.

Every call here is read-only (GET) against real production data - no
create/update/delete against a live tenant.
"""
import os

import pytest

from sasci360solexecute.base import CI360ExecuteBase, CI360ExecuteConfig

_HOST = os.environ.get("CI360_HOST")
_SECRET_KEY = os.environ.get("CI360_SECRET_KEY")
_TENANT_ID = os.environ.get("CI360_TENANT_ID")


def _full_host():
    """CI360_HOST is documented as a bare hostname (e.g.
    extapigwservice-<env>.ci360.sas.com); this client's config needs the
    full https:// URL. Accept either so the same env var value works
    across every package's live-tenant tests."""
    if _HOST and not _HOST.startswith("http"):
        return "https://{0}".format(_HOST)
    return _HOST


pytestmark = pytest.mark.skipif(
    not (_HOST and _SECRET_KEY and _TENANT_ID),
    reason="CI360_HOST, CI360_SECRET_KEY, and CI360_TENANT_ID must all be set to run live-tenant tests",
)


@pytest.fixture
def client():
    config = CI360ExecuteConfig(host=_full_host(), secret_key=_SECRET_KEY, tenant_id=_TENANT_ID)
    return CI360ExecuteBase(config)


def test_authenticates_and_validates_connection(client):
    assert client.validate_connection() is True


def test_get_batch_jobs_returns_a_real_response(client):
    result = client.get_batch_jobs(limit=1)

    assert isinstance(result, dict)


def test_get_scheduled_jobs_returns_a_real_response(client):
    result = client.get_scheduled_jobs(limit=1)

    assert isinstance(result, dict)
