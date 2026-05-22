# -*- coding: utf-8 -*-
"""Shared backend contract: identity query over configured resources."""

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
        ("TCPIP::HISLIP", "transport.hislip"),
        ("TCPIP::SOCKET", "transport.socket"),
        ("USB::INSTR", "transport.usb"),
    ],
)
def test_identity_query_contract(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_command_map,
    apply_pyvisa_contract_policy,
):
    """Verify that an identity query succeeds on supported configured transports."""
    contract_id = f"identity.query.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    query_cmd = pyvisa_command_map.get("identity_query", "*IDN?")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        instr = rm.open_resource(resource_name)
        try:
            response = instr.query(query_cmd).strip()
        finally:
            instr.close()
    finally:
        rm.close()

    expected = require_pyvisa_profile.expected_idn
    assert response, "Identity query returned an empty response"
    if expected:
        assert response == expected
