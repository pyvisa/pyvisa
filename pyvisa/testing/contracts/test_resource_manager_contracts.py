# -*- coding: utf-8 -*-
"""Shared resource-manager contracts for backend implementations."""

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
    ],
)
def test_resource_manager_lists_profile_resources(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
):
    """Configured resources should be visible from ResourceManager.list_resources."""
    contract_id = f"resource_manager.listed.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        visible = rm.list_resources()
    finally:
        rm.close()

    assert resource_name in visible


@pytest.mark.parametrize(
    "resource_key, capability_key",
    [
        ("TCPIP::INSTR", "transport.vxi11"),
        ("TCPIP::HISLIP", "transport.hislip"),
        ("TCPIP::SOCKET", "transport.socket"),
    ],
)
def test_resource_manager_open_close_contract(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
):
    """Configured resources can be opened and closed successfully."""
    contract_id = f"resource_manager.open_close.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        instr = rm.open_resource(resource_name)
        instr.close()
    finally:
        rm.close()


@pytest.mark.parametrize(
    "resource_key, capability_key, expected_class",
    [
        ("TCPIP::INSTR", "transport.vxi11", "INSTR"),
        ("TCPIP::HISLIP", "transport.hislip", "INSTR"),
        ("TCPIP::SOCKET", "transport.socket", "SOCKET"),
    ],
)
def test_resource_manager_resource_info_contract(
    resource_key: str,
    capability_key: str,
    expected_class: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
):
    """Configured resources expose coherent class information via resource_info."""
    contract_id = f"resource_manager.info.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        info = rm.resource_info(resource_name)
    finally:
        rm.close()

    assert info is not None
    assert info.resource_class == expected_class
