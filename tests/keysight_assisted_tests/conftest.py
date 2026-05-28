# -*- coding: utf-8 -*-
"""Pytest fixtures and profile helpers for Keysight-assisted tests."""

from __future__ import annotations

import os

from pyvisa.testing import (
    CapabilityFlags,
    CommandMap,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
)


def keysight_profile_from_env() -> InstrumentProfile | None:
    """Build an IVI profile from Keysight virtual instrument settings."""
    setting = os.environ.get("PYVISA_KEYSIGHT_VIRTUAL_INSTR")
    if setting is None:
        return None

    if setting == "0":
        addresses = ResourceAddresses(
            tcpip_instr="TCPIP::127.0.0.1::INSTR",
            tcpip_socket="TCPIP::127.0.0.1::5025::SOCKET",
        )
    else:
        addresses = ResourceAddresses(
            tcpip_instr="TCPIP::192.168.0.2::INSTR",
            tcpip_socket="TCPIP::192.168.0.2::5025::SOCKET",
        )

    return InstrumentProfile(
        name="keysight-virtual-instr",
        resource_addresses=addresses,
        command_map=CommandMap(
            identity_query="*IDN?",
            shared_query="QUERY?",
            health_query="SYST:HEALTH?",
            binary_query_template="DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        ),
        capabilities=CapabilityFlags(
            transport_vxi11=True,
            transport_socket=True,
            transport_hislip=False,
            transport_usb=False,
        ),
        metadata=ProfileMetadata(
            source="pyvisa-tests",
            backend="ivi",
            target="keysight",
        ),
    )
