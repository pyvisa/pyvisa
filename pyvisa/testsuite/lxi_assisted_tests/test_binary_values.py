# -*- coding: utf-8 -*-
"""Binary transfer tests for LXI-assisted TCPIP INSTR resources."""

import pytest

from pyvisa import ResourceManager
from pyvisa.testsuite import require_visa_lib

from . import (
    RESOURCE_ADDRESSES,
    require_lxi_assisted,
    require_lxi_hislip,
    require_lxi_vxi11,
)

pytestmark = [require_visa_lib, require_lxi_assisted]


def _open_instr(resource_name: str):
    rm = ResourceManager()
    if "hislip" in resource_name.lower() and rm.visalib.library_path == "py":
        rm.close()
        pytest.skip("pyvisa-py does not support HiSLIP")

    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    instr.read_termination = ""
    instr.write_termination = "\n"
    return rm, instr


def _require_binary_commands(instr):
    try:
        health = instr.query("SYST:HEALTH?").strip().lower()
    except Exception:
        pytest.skip("Fake instrument does not expose SYST:HEALTH?")

    if "data=asc,bin" not in health:
        pytest.skip("Fake instrument does not expose DATA:BIN? command family")


@pytest.mark.parametrize(
    "resource_name",
    [
        pytest.param(RESOURCE_ADDRESSES["TCPIP::INSTR"], marks=require_lxi_vxi11),
        pytest.param(RESOURCE_ADDRESSES["TCPIP::HISLIP"], marks=require_lxi_hislip),
    ],
)
def test_query_binary_values_with_ieee_header(resource_name):
    rm, instr = _open_instr(resource_name)
    try:
        _require_binary_commands(instr)
        values = instr.query_binary_values(
            "DATA:BIN? u16,4,le,ieee,none,ramp,1",
            datatype="H",
            is_big_endian=False,
            header_fmt="ieee",
            expect_termination=False,
        )
        assert values == [0, 1, 2, 3]
    finally:
        instr.close()
        rm.close()


@pytest.mark.parametrize(
    "resource_name",
    [
        pytest.param(RESOURCE_ADDRESSES["TCPIP::INSTR"], marks=require_lxi_vxi11),
        pytest.param(RESOURCE_ADDRESSES["TCPIP::HISLIP"], marks=require_lxi_hislip),
    ],
)
def test_query_binary_values_with_hp_header(resource_name):
    rm, instr = _open_instr(resource_name)
    try:
        _require_binary_commands(instr)
        values = instr.query_binary_values(
            "DATA:BIN? u16,4,be,hp,none,ramp,1",
            datatype="H",
            is_big_endian=True,
            header_fmt="hp",
            expect_termination=False,
        )
        assert values == [0, 1, 2, 3]
    finally:
        instr.close()
        rm.close()


@pytest.mark.parametrize(
    "resource_name",
    [
        pytest.param(RESOURCE_ADDRESSES["TCPIP::INSTR"], marks=require_lxi_vxi11),
        pytest.param(RESOURCE_ADDRESSES["TCPIP::HISLIP"], marks=require_lxi_hislip),
    ],
)
def test_query_binary_values_empty_header_with_termination(resource_name):
    rm, instr = _open_instr(resource_name)
    try:
        _require_binary_commands(instr)
        values = instr.query_binary_values(
            "DATA:BIN? u16,4,le,empty,lf,ramp,1",
            datatype="H",
            is_big_endian=False,
            header_fmt="empty",
            expect_termination=True,
            data_points=4,
        )
        assert values == [0, 1, 2, 3]
    finally:
        instr.close()
        rm.close()
