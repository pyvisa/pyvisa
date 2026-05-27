# -*- coding: utf-8 -*-
"""Shared resource-manager contracts for backend implementations."""

from __future__ import annotations

import pytest

from pyvisa.testing.contracts._resource_matrix import (
    ALL_RESOURCE_SPECS,
    ResourceSpec,
    contract_params,
)
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


@pytest.mark.parametrize("resource_spec", contract_params(ALL_RESOURCE_SPECS))
def test_resource_manager_lists_profile_resources(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Configured resources should be visible from ResourceManager.list_resources."""
    contract_id = f"resource_manager.listed.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(resource_spec.capability_key, True):
        pytest.skip(
            f"Capability {resource_spec.capability_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.get(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    visible = pyvisa_resource_manager.list_resources()

    assert resource_name in visible


@pytest.mark.parametrize("resource_spec", contract_params(ALL_RESOURCE_SPECS))
def test_resource_manager_open_close_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Configured resources can be opened and closed successfully."""
    contract_id = f"resource_manager.open_close.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(resource_spec.capability_key, True):
        pytest.skip(
            f"Capability {resource_spec.capability_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.get(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    instr = pyvisa_resource_manager.open_resource(resource_name)
    instr.close()


@pytest.mark.parametrize("resource_spec", contract_params(ALL_RESOURCE_SPECS))
def test_resource_manager_resource_info_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Configured resources expose coherent class information via resource_info."""
    contract_id = f"resource_manager.info.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(resource_spec.capability_key, True):
        pytest.skip(
            f"Capability {resource_spec.capability_key} is disabled for this backend/profile"
        )

    resource_name = require_pyvisa_profile.resource_addresses.get(
        resource_spec.resource_key
    )
    if not resource_name:
        pytest.skip(
            f"Profile does not define resource address for {resource_spec.resource_key}"
        )

    info = pyvisa_resource_manager.resource_info(resource_name)

    assert info is not None
    assert info.resource_class == resource_spec.expected_class
