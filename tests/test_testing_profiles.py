# -*- coding: utf-8 -*-
"""Unit tests for typed testing-profile dataclasses."""

from __future__ import annotations

import pytest

from pyvisa.testing import (
    AsrlResourceCapabilities,
    BaseResourceCapabilities,
    CapabilityFlags,
    CommandMap,
    GpibCapabilities,
    MessageBasedResourceCapabilities,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
    TcpipCapabilities,
    UsbResourceCapabilities,
)


def test_instrument_profile_uses_explicit_typed_fields():
    addresses = ResourceAddresses(tcpip_instr="TCPIP::127.0.0.1::INSTR")
    command_map = CommandMap(identity_query="*IDN?")
    capabilities = CapabilityFlags(
        tcpip=TcpipCapabilities(
            vxi11=MessageBasedResourceCapabilities(query=True),
        )
    )
    metadata = ProfileMetadata(
        source="env", target="pyvisa-tester", extras={"extra": 3}
    )

    profile = InstrumentProfile(
        name="sample",
        resource_addresses=addresses,
        command_map=command_map,
        capabilities=capabilities,
        metadata=metadata,
    )

    assert isinstance(profile.resource_addresses, ResourceAddresses)
    assert isinstance(profile.command_map, CommandMap)
    assert isinstance(profile.capabilities, CapabilityFlags)
    assert isinstance(profile.metadata, ProfileMetadata)

    assert profile.resource_addresses.tcpip_instr == "TCPIP::127.0.0.1::INSTR"
    assert profile.command_map.identity_query == "*IDN?"
    assert (
        profile.capabilities.transport_enabled_for_resource("TCPIP::INSTR", False)
        is True
    )
    assert profile.capabilities.resource_feature("TCPIP::INSTR", "query", False) is True
    assert profile.metadata.source == "env"
    assert profile.metadata.target == "pyvisa-tester"
    assert profile.metadata.extras["extra"] == 3


def test_instrument_profile_rejects_plain_mappings():
    with pytest.raises(TypeError, match="resource_addresses"):
        InstrumentProfile(
            name="sample",
            resource_addresses={"TCPIP::INSTR": "TCPIP::127.0.0.1::INSTR"},
            command_map=CommandMap(identity_query="*IDN?"),
            capabilities=CapabilityFlags(
                tcpip=TcpipCapabilities(vxi11=MessageBasedResourceCapabilities())
            ),
            metadata=ProfileMetadata(source="env", target="pyvisa-tester"),
        )


def test_instrument_profile_rejects_non_command_map():
    with pytest.raises(TypeError, match="command_map"):
        InstrumentProfile(
            name="sample",
            resource_addresses=ResourceAddresses(tcpip_instr="TCPIP::127.0.0.1::INSTR"),
            command_map={"identity_query": "*IDN?"},
            capabilities=CapabilityFlags(
                tcpip=TcpipCapabilities(vxi11=MessageBasedResourceCapabilities())
            ),
            metadata=ProfileMetadata(source="env", target="pyvisa-tester"),
        )


def test_instrument_profile_rejects_non_capability_flags():
    with pytest.raises(TypeError, match="capabilities"):
        InstrumentProfile(
            name="sample",
            resource_addresses=ResourceAddresses(tcpip_instr="TCPIP::127.0.0.1::INSTR"),
            command_map=CommandMap(identity_query="*IDN?"),
            capabilities={"transport.vxi11": True},
            metadata=ProfileMetadata(source="env", target="pyvisa-tester"),
        )


def test_instrument_profile_rejects_non_metadata():
    with pytest.raises(TypeError, match="metadata"):
        InstrumentProfile(
            name="sample",
            resource_addresses=ResourceAddresses(tcpip_instr="TCPIP::127.0.0.1::INSTR"),
            command_map=CommandMap(identity_query="*IDN?"),
            capabilities=CapabilityFlags(
                tcpip=TcpipCapabilities(
                    vxi11=BaseResourceCapabilities(query=True),
                )
            ),
            metadata={"target": "pyvisa-tester"},
        )


def test_capability_flags_overlay_merges_transports_and_features():
    base = CapabilityFlags(
        tcpip=TcpipCapabilities(
            vxi11=BaseResourceCapabilities(query=True, timeout=True, locking=True),
        ),
        usb=UsbResourceCapabilities(supported=False),
    )
    override = CapabilityFlags(
        tcpip=TcpipCapabilities(
            vxi11=BaseResourceCapabilities(locking=False),
        ),
        asrl=AsrlResourceCapabilities(supported=True),
        gpib=GpibCapabilities(enabled=False),
    )

    merged = base.overlay(override)

    assert merged.transport_enabled_for_resource("TCPIP::INSTR", False)
    assert merged.transport_enabled_for_resource("GPIB::INSTR", True) is False
    assert merged.transport_enabled_for_resource("USB::INSTR", True) is False
    assert merged.transport_enabled_for_resource("ASRL::INSTR", False)
    assert merged.resource_feature("TCPIP::INSTR", "query", False)
    assert merged.resource_feature("TCPIP::INSTR", "timeout", False)
    assert merged.resource_feature("TCPIP::INSTR", "locking", True) is False


def test_profile_metadata_to_dict_merges_canonical_and_extra_fields():
    metadata = ProfileMetadata(
        source="pyvisa-tests",
        target="keysight",
        backend="ivi",
        extras={"custom": "value"},
    )

    data = metadata.to_dict()

    assert data["source"] == "pyvisa-tests"
    assert data["target"] == "keysight"
    assert data["backend"] == "ivi"
    assert data["custom"] == "value"
