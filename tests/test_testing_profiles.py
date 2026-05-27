# -*- coding: utf-8 -*-
"""Unit tests for typed testing-profile dataclasses."""

from __future__ import annotations

from pyvisa.testing import (
    CapabilityFlags,
    CommandMap,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
)


def test_instrument_profile_coerces_mapping_fields_to_typed_dataclasses():
    profile = InstrumentProfile(
        name="sample",
        resource_addresses={"TCPIP::INSTR": "TCPIP::127.0.0.1::INSTR"},
        command_map={"identity_query": "*IDN?"},
        capabilities={"transport.vxi11": 1},
        metadata={"source": "env", "target": "pyvisa-tester", "extra": 3},
    )

    assert isinstance(profile.resource_addresses, ResourceAddresses)
    assert isinstance(profile.command_map, CommandMap)
    assert isinstance(profile.capabilities, CapabilityFlags)
    assert isinstance(profile.metadata, ProfileMetadata)

    assert profile.resource_addresses["TCPIP::INSTR"] == "TCPIP::127.0.0.1::INSTR"
    assert profile.command_map["identity_query"] == "*IDN?"
    assert profile.capabilities["transport.vxi11"] is True
    assert profile.metadata["source"] == "env"
    assert profile.metadata["target"] == "pyvisa-tester"
    assert profile.metadata["extra"] == 3


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
