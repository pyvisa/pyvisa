# -*- coding: utf-8 -*-
"""Shared Keysight-style TCPIP contracts for backend implementations."""

from __future__ import annotations

import pytest

from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


@pytest.mark.parametrize(
    "resource_key, capability_key",
    [
        ("TCPIP::INSTR", "transport.vxi11"),
        ("TCPIP::SOCKET", "transport.socket"),
    ],
)
def test_keysight_tcpip_query_contract(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_command_map,
    apply_pyvisa_contract_policy,
):
    """Validate identity and query semantics over supported TCPIP transports."""
    contract_id = f"keysight.tcpip.query.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    idn_cmd = pyvisa_command_map.get("identity_query", "*IDN?")
    query_cmd = pyvisa_command_map.get("shared_query", "QUERY?")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        instr = rm.open_resource(resource_name)
        try:
            idn = instr.query(idn_cmd).strip()
            answer = instr.query(query_cmd).strip()
        finally:
            instr.close()
    finally:
        rm.close()

    expected_idn = require_pyvisa_profile.expected_idn
    assert idn
    if expected_idn:
        assert idn == expected_idn
    assert answer == "RESPONSE"
