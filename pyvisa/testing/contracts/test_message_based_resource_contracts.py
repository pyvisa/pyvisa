# -*- coding: utf-8 -*-
"""Shared contracts for message-based resource behavior across transports."""

from __future__ import annotations

import pytest

from pyvisa.testing import CapabilityFlags, CommandMap
from pyvisa.testing.contracts._command_helpers import require_command
from pyvisa.testing.contracts._resource_matrix import (
    MESSAGE_BASED_RESOURCE_SPECS,
    ResourceSpec,
    contract_params,
)
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


def _capability_or_default(
    capabilities: CapabilityFlags, attr_name: str, default: bool
) -> bool:
    value = getattr(capabilities, attr_name)
    return default if value is None else bool(value)


def _query_capability_key(resource_spec: ResourceSpec) -> str:
    return resource_spec.query_capability_attr or (
        f"resource_query_{resource_spec.contract_suffix.replace('::', '_')}"
    )


def _configure_query_terminations(resource_spec: ResourceSpec, instrument) -> None:
    if resource_spec.resource_key in {"TCPIP::SOCKET", "ASRL::INSTR"}:
        instrument.read_termination = "\n"
    else:
        instrument.read_termination = ""
    instrument.write_termination = "\n"


@pytest.mark.parametrize("resource_spec", contract_params(MESSAGE_BASED_RESOURCE_SPECS))
def test_message_based_shared_query_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    pyvisa_command_map: CommandMap,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Validate shared text query behavior for message-based resource classes."""
    contract_id = f"message_based.query.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not _capability_or_default(
        pyvisa_backend_capabilities, resource_spec.transport_capability_attr, True
    ):
        pytest.skip(
            f"Capability {resource_spec.transport_capability_attr} is disabled for this backend/profile"
        )

    query_capability_key = _query_capability_key(resource_spec)
    if not _capability_or_default(
        pyvisa_backend_capabilities,
        query_capability_key,
        resource_spec.default_query_enabled,
    ):
        pytest.skip(
            f"Capability {query_capability_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.for_resource(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    query_cmd = require_command(pyvisa_command_map, "shared_query")
    rm = pyvisa_resource_manager
    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    try:
        _configure_query_terminations(resource_spec, instr)
        response = instr.query(query_cmd).strip()
    finally:
        instr.close()

    assert response == "RESPONSE"


@pytest.mark.parametrize("resource_spec", contract_params(MESSAGE_BASED_RESOURCE_SPECS))
def test_message_based_timeout_attribute_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Validate timeout round-trip on message-based resource classes."""
    contract_id = f"message_based.timeout.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not _capability_or_default(
        pyvisa_backend_capabilities, resource_spec.transport_capability_attr, True
    ):
        pytest.skip(
            f"Capability {resource_spec.transport_capability_attr} is disabled for this backend/profile"
        )

    timeout_capability_key = (
        f"resource_timeout_{resource_spec.contract_suffix.replace('::', '_')}"
    )
    if not _capability_or_default(
        pyvisa_backend_capabilities, timeout_capability_key, True
    ):
        pytest.skip(
            f"Capability {timeout_capability_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.for_resource(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    rm = pyvisa_resource_manager
    instr = rm.open_resource(resource_name)
    try:
        instr.timeout = 1500
        assert instr.timeout == 1500
    finally:
        instr.close()
