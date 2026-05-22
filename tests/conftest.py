# -*- coding: utf-8 -*-
"""Global pytest configuration for the top-level PyVISA test tree."""

from __future__ import annotations

import os

import pytest

from pyvisa.testing import InstrumentProfile

pytest_plugins = ("pyvisa.testing.pytest_plugin",)


def _keysight_profile_from_env() -> InstrumentProfile | None:
    """Build an IVI profile from Keysight virtual instrument settings."""
    setting = os.environ.get("PYVISA_KEYSIGHT_VIRTUAL_INSTR")
    if setting is None:
        return None

    if setting == "0":
        addresses = {
            "TCPIP::INSTR": "TCPIP::127.0.0.1::INSTR",
            "TCPIP::SOCKET": "TCPIP::127.0.0.1::5025::SOCKET",
        }
    else:
        addresses = {
            "TCPIP::INSTR": "TCPIP::192.168.0.2::INSTR",
            "TCPIP::SOCKET": "TCPIP::192.168.0.2::5025::SOCKET",
        }

    return InstrumentProfile(
        name="keysight-virtual-instr",
        resource_addresses=addresses,
        command_map={
            "identity_query": "*IDN?",
            "shared_query": "QUERY?",
            "health_query": "SYST:HEALTH?",
            "binary_query_template": "DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        },
        capabilities={
            "transport.vxi11": True,
            "transport.socket": True,
            "transport.hislip": False,
            "transport.usb": False,
        },
        metadata={"source": "pyvisa-tests", "backend": "ivi", "target": "keysight"},
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyvisa_select_profile(
    config: pytest.Config, profile_name: str
) -> InstrumentProfile | None:
    """Provide pyvisa-owned IVI profile selection for Keysight runs.

    Returning ``None`` preserves the default env profile provider used for
    pyvisa-tester-driven runs.
    """
    _ = config
    if profile_name in ("env", "keysight"):
        return _keysight_profile_from_env()
    return None
