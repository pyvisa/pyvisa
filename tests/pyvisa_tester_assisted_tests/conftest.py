# -*- coding: utf-8 -*-
"""Pytest fixtures for pyvisa-tester-assisted tests."""

from __future__ import annotations

from collections.abc import Callable
import os

import pytest


@pytest.fixture
def require_pyvisa_tester_profile(require_pyvisa_profile):
    """Require a resolved profile targeting the pyvisa-tester fake instrument stack."""
    if os.environ.get("PYVISA_TESTER_ASSISTED") != "1":
        pytest.skip("Set PYVISA_TESTER_ASSISTED=1 to run pyvisa-tester-assisted tests")

    target = str(require_pyvisa_profile.metadata.target or "").strip().lower()
    if target != "pyvisa-tester":
        pytest.skip("Assisted tests require a profile targeting pyvisa-tester")
    return require_pyvisa_profile


@pytest.fixture
def require_assisted_resource(
    require_pyvisa_tester_profile,
    pyvisa_backend_capabilities,
) -> Callable[[str], str]:
    """Return the configured resource address for a supported assisted resource key."""

    def _require(resource_key: str) -> str:
        capability_enabled = pyvisa_backend_capabilities.transport_enabled_for_resource(
            resource_key, True
        )
        if not capability_enabled:
            pytest.skip(
                f"Transport for {resource_key} is disabled for this backend/profile"
            )

        resource_name = require_pyvisa_tester_profile.resource_addresses.for_resource(
            resource_key
        )
        if not resource_name:
            pytest.skip(f"Profile does not define resource address for {resource_key}")

        return resource_name

    return _require


@pytest.fixture
def require_assisted_command(require_pyvisa_tester_profile) -> Callable[[str], str]:
    """Return required semantic command mappings from the selected profile."""

    def _require(command_key: str) -> str:
        try:
            command = require_pyvisa_tester_profile.command_map.require(command_key)
        except KeyError:
            pytest.fail(
                f"Profile does not define required command mapping {command_key!r}"
            )
        return str(command)

    return _require
