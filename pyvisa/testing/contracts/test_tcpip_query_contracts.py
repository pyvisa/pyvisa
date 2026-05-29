# -*- coding: utf-8 -*-
"""Shared TCPIP query contracts for backend implementations."""

from __future__ import annotations

import pytest

from pyvisa.testing import CapabilityFlags, CommandMap
from pyvisa.testing.contracts._command_helpers import require_command
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


@pytest.mark.parametrize(
    "resource_key, transport_key",
    [
        ("TCPIP::INSTR", "vxi11"),
        ("TCPIP::SOCKET", "socket"),
    ],
)
def test_tcpip_query_contract(
    resource_key: str,
    transport_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    pyvisa_command_map: CommandMap,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Validate identity and query semantics over supported TCPIP transports."""
    contract_id = f"tcpip.query.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    capability_enabled = pyvisa_backend_capabilities.transport_enabled_for_resource(
        resource_key,
        True,
    )
    if not capability_enabled:
        pytest.skip(f"Transport {transport_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.for_resource(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    idn_cmd = require_command(pyvisa_command_map, "identity_query")
    query_cmd = require_command(pyvisa_command_map, "shared_query")

    rm = pyvisa_resource_manager
    instr = rm.open_resource(resource_name)
    try:
        idn = instr.query(idn_cmd).strip()
        answer = instr.query(query_cmd).strip()
    finally:
        instr.close()

    expected_idn = require_pyvisa_profile.expected_idn
    assert idn
    if expected_idn:
        assert idn == expected_idn
    assert answer == "RESPONSE"
