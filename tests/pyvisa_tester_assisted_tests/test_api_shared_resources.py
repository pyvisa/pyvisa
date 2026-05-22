# -*- coding: utf-8 -*-
"""Transport-shared API-level assisted tests.

These tests intentionally use only pyvisa public API and run across transports
where capabilities overlap.
"""

from __future__ import annotations

import importlib
from contextlib import nullcontext

import pytest

from pyvisa.testing.requirements import require_visa_lib

from . import (
    EXPECTED_IDN,
    RESOURCE_ADDRESSES,
    require_backend_py,
    require_pyvisa_tester_assisted,
    require_transport_hislip,
    require_transport_socket,
    require_transport_usb,
    require_transport_vxi11,
)

pytestmark = [
    require_visa_lib,
    require_pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_shared,
]


def _open_resource_for_transport(resource_key: str):
    from pyvisa import ResourceManager

    if resource_key == "USB::INSTR":
        usb_mock = pytest.importorskip("pyvisa_tester.usb_mock")
        ctx = usb_mock.patched_pyusb()
        ctx.__enter__()
        import pyvisa_py.usb as pyvisa_py_usb

        importlib.reload(pyvisa_py_usb)
    else:
        ctx = nullcontext()
        ctx.__enter__()

    rm = ResourceManager()
    if resource_key == "TCPIP::HISLIP" and rm.visalib.library_path == "py":
        rm.close()
        ctx.__exit__(None, None, None)
        pytest.skip("pyvisa-py does not support HiSLIP")

    instr = rm.open_resource(RESOURCE_ADDRESSES[resource_key])
    instr.timeout = 2000
    if resource_key == "TCPIP::SOCKET":
        instr.read_termination = "\n"
        instr.write_termination = "\n"
    else:
        instr.read_termination = ""
        instr.write_termination = "\n"
    return ctx, rm, instr


@pytest.mark.parametrize(
    "resource_key",
    [
        pytest.param("TCPIP::INSTR", marks=require_transport_vxi11),
        pytest.param("TCPIP::HISLIP", marks=require_transport_hislip),
        pytest.param("TCPIP::SOCKET", marks=require_transport_socket),
        pytest.param(
            "USB::INSTR",
            marks=[
                require_transport_usb,
                require_backend_py,
                pytest.mark.pyvisa_tester_usb,
            ],
        ),
    ],
)
def test_shared_idn_and_query(resource_key):
    ctx, rm, instr = _open_resource_for_transport(resource_key)
    try:
        assert instr.query("*IDN?").strip() == EXPECTED_IDN
        assert instr.query("QUERY?").strip() == "RESPONSE"
    finally:
        instr.close()
        rm.close()
        ctx.__exit__(None, None, None)


@pytest.mark.parametrize(
    "resource_key",
    [
        pytest.param("TCPIP::INSTR", marks=require_transport_vxi11),
        pytest.param("TCPIP::HISLIP", marks=require_transport_hislip),
        pytest.param(
            "USB::INSTR",
            marks=[
                require_transport_usb,
                require_backend_py,
                pytest.mark.pyvisa_tester_usb,
            ],
        ),
    ],
)
def test_shared_binary_query(resource_key):
    ctx, rm, instr = _open_resource_for_transport(resource_key)
    try:
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
        ctx.__exit__(None, None, None)
