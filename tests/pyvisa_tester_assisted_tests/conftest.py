# -*- coding: utf-8 -*-
"""Pytest fixtures for pyvisa-tester-assisted tests."""

from __future__ import annotations

from collections.abc import Callable
import os

import pytest

_RESOURCE_CAPABILITY_KEYS = {
    "TCPIP::INSTR": "transport.vxi11",
    "TCPIP::HISLIP": "transport.hislip",
    "TCPIP::SOCKET": "transport.socket",
    "USB::INSTR": "transport.usb",
    "GPIB::INSTR": "transport.gpib",
    "GPIB::INTFC": "transport.gpib",
    "ASRL::INSTR": "transport.asrl",
}


@pytest.fixture(scope="session")
def require_pyvisa_tester_profile(require_pyvisa_profile):
    """Require a resolved profile targeting the pyvisa-tester fake instrument stack."""
    if os.environ.get("PYVISA_TESTER_ASSISTED") != "1":
        pytest.skip("Set PYVISA_TESTER_ASSISTED=1 to run pyvisa-tester-assisted tests")

    target = str(require_pyvisa_profile.metadata.target or "").strip().lower()
    if target != "pyvisa-tester":
        pytest.skip("Assisted tests require a profile targeting pyvisa-tester")
    return require_pyvisa_profile


@pytest.fixture(scope="session")
def require_assisted_resource(
    require_pyvisa_tester_profile,
    pyvisa_backend_capabilities,
) -> Callable[[str], str]:
    """Return the configured resource address for a supported assisted resource key."""

    def _require(resource_key: str) -> str:
        capability_key = _RESOURCE_CAPABILITY_KEYS.get(resource_key)
        if capability_key and not pyvisa_backend_capabilities.get(capability_key, True):
            pytest.skip(
                f"Capability {capability_key} is disabled for this backend/profile"
            )

        resource_name = require_pyvisa_tester_profile.resource_addresses.get(
            resource_key
        )
        if not resource_name:
            pytest.skip(f"Profile does not define resource address for {resource_key}")

        return resource_name

    return _require


@pytest.fixture(scope="session")
def require_assisted_command(require_pyvisa_tester_profile) -> Callable[[str], str]:
    """Return required semantic command mappings from the selected profile."""

    def _require(command_key: str) -> str:
        try:
            command = require_pyvisa_tester_profile.command_map[command_key]
        except KeyError:
            pytest.fail(
                f"Profile does not define required command mapping {command_key!r}"
            )
        return str(command)

    return _require
