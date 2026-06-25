# -*- coding: utf-8 -*-
"""Shared backend contract: identity query over configured resources."""

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


def _transport_or_default(
    capabilities: CapabilityFlags,
    resource_spec: ResourceSpec,
    default: bool,
) -> bool:
    return capabilities.transport_enabled_for_resource(
        resource_spec.resource_key, default
    )


def _resource_feature_or_default(
    capabilities: CapabilityFlags,
    resource_spec: ResourceSpec,
    feature_name: str,
    default: bool,
) -> bool:
    return capabilities.resource_feature(
        resource_spec.resource_key, feature_name, default
    )


@pytest.mark.parametrize("resource_spec", contract_params(MESSAGE_BASED_RESOURCE_SPECS))
def test_identity_query_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    pyvisa_command_map: CommandMap,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Verify that an identity query succeeds on supported configured transports."""
    contract_id = f"identity.query.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not _transport_or_default(pyvisa_backend_capabilities, resource_spec, True):
        pytest.skip(
            f"Transport {resource_spec.transport_key} is disabled for this backend/profile"
        )

    if not _resource_feature_or_default(
        pyvisa_backend_capabilities,
        resource_spec,
        "query",
        resource_spec.default_query_enabled,
    ):
        pytest.skip(
            f"Query support for {resource_spec.resource_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.for_resource(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    query_cmd = require_command(pyvisa_command_map, "identity_query")

    rm = pyvisa_resource_manager
    try:
        instr = rm.open_resource(resource_name)
        try:
            response = instr.query(query_cmd).strip()
        finally:
            instr.close()
    finally:
        pass

    expected = require_pyvisa_profile.expected_idn
    assert response, "Identity query returned an empty response"
    if expected:
        assert response == expected
