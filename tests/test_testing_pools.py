# -*- coding: utf-8 -*-
"""Unit tests for shared instrument-pool selection."""

from __future__ import annotations

from pyvisa.testing import InstrumentProfile
from pyvisa.testing.env_profile import profile_from_environment
from pyvisa.testing.pools import (
    CommandMapInstrumentPool,
    PyvisaTesterTcpipInstrumentPool,
    build_default_instrument_pool,
)


def test_profile_from_environment_marks_pyvisa_tester_target(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYVISA_TESTER_ASSISTED", "1")

    profile = profile_from_environment()

    assert profile is not None
    assert profile.metadata["target"] == "pyvisa-tester"


def test_default_instrument_pool_prefers_pyvisa_tester_pool():
    profile = InstrumentProfile(
        name="pyvisa-tester-env",
        resource_addresses={
            "TCPIP::INSTR": "TCPIP::127.0.0.1::inst0::INSTR",
            "TCPIP::HISLIP": "TCPIP::127.0.0.1::hislip0::INSTR",
            "TCPIP::SOCKET": "TCPIP::127.0.0.1::5025::SOCKET",
            "USB::INSTR": "USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR",
        },
        metadata={"source": "env", "target": "pyvisa-tester"},
    )

    pool = build_default_instrument_pool(
        profile,
        {
            "binary_query_template": "BROKEN {datatype}",
            "binary_configure_template": "BROKEN-CFG {datatype}",
            "binary_read_query": "BROKEN-READ?",
            "error_query": "BROKEN:ERR?",
            "health_query": "BROKEN:HEALTH?",
        },
    )

    assert isinstance(pool, PyvisaTesterTcpipInstrumentPool)
    assert pool.supports_resource("TCPIP::INSTR")
    assert pool.supports_resource("TCPIP::HISLIP")
    assert pool.supports_resource("TCPIP::SOCKET")
    assert not pool.supports_resource("USB::INSTR")

    facet = pool.for_resource("TCPIP::INSTR")
    assert facet.health_query() == "SYST:HEALTH?"
    assert (
        facet.binary_query(
            datatype="u16",
            count=4,
            endian="le",
            header="ieee",
            termination="none",
            pattern="ramp",
            start=1,
        )
        == "DATA:BIN? u16,4,le,ieee,none,ramp,1"
    )
    assert (
        facet.binary_configure(
            datatype="u16",
            count=4,
            endian="be",
            header="hp",
            termination="lf",
            pattern="rand",
            start=7,
        )
        == "DATA:BIN:CFG u16,4,be,hp,lf,rand,7"
    )
    assert facet.binary_read_query() == "DATA:BIN:READ?"


def test_default_instrument_pool_falls_back_to_command_map_pool():
    profile = InstrumentProfile(
        name="generic",
        resource_addresses={"TCPIP::INSTR": "TCPIP::192.168.0.2::INSTR"},
        metadata={"target": "keysight"},
    )

    pool = build_default_instrument_pool(
        profile,
        {
            "binary_query_template": "QUERY {datatype},{count}",
        },
    )

    assert isinstance(pool, CommandMapInstrumentPool)
    facet = pool.for_resource("TCPIP::INSTR")
    assert (
        facet.binary_query(
            datatype="u16",
            count=4,
            endian="le",
            header="ieee",
            termination="none",
            pattern="ramp",
            start=1,
        )
        == "QUERY u16,4"
    )
