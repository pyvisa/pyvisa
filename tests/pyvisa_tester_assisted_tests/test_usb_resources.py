# -*- coding: utf-8 -*-
"""USB assisted tests through pyvisa API (pyvisa-py backend only)."""

import importlib

import pytest

from pyvisa.testing.requirements import require_visa_lib

from . import (
    EXPECTED_IDN,
    RESOURCE_ADDRESSES,
    require_backend_py,
    require_pyvisa_tester_assisted,
    require_transport_usb,
)

pytestmark = [
    require_visa_lib,
    require_pyvisa_tester_assisted,
    require_backend_py,
    require_transport_usb,
    pytest.mark.pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_usb,
]


def _open_usb_resource():
    usb_mock = pytest.importorskip("pyvisa_tester.usb_mock")
    from pyvisa import ResourceManager

    ctx = usb_mock.patched_pyusb()
    ctx.__enter__()

    # If pyvisa_py.usb is imported without a valid backend, USB sessions are
    # registered as unavailable. Import/reload it under monkeypatch context.
    import pyvisa_py.usb as pyvisa_py_usb

    importlib.reload(pyvisa_py_usb)

    rm = ResourceManager()
    try:
        instr = rm.open_resource(RESOURCE_ADDRESSES["USB::INSTR"])
    except Exception:
        rm.close()
        ctx.__exit__(None, None, None)
        raise

    instr.timeout = 1000
    instr.read_termination = ""
    instr.write_termination = "\n"
    return ctx, rm, instr


def test_usb_query_idn_via_pyvisa_api():
    ctx, rm, instr = _open_usb_resource()
    try:
        assert instr.query("*IDN?").strip() == EXPECTED_IDN
        assert instr.query("QUERY?").strip() == "RESPONSE"
    finally:
        instr.close()
        rm.close()
        ctx.__exit__(None, None, None)


def test_usb_binary_values_via_pyvisa_api():
    ctx, rm, instr = _open_usb_resource()
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
