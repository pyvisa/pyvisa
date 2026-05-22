# -*- coding: utf-8 -*-
"""pyvisa-tester-assisted tests for multiple transports and backends."""

import functools
import os
import types

import pytest

from .env_helpers import load_tester_env_from_file

load_tester_env_from_file()

_ASSISTED_AVAILABLE = os.environ.get("PYVISA_TESTER_ASSISTED") == "1"
_VXI11_AVAILABLE = (
    _ASSISTED_AVAILABLE and os.environ.get("PYVISA_TESTER_VXI11", "1") != "0"
)
_HISLIP_AVAILABLE = (
    _ASSISTED_AVAILABLE and os.environ.get("PYVISA_TESTER_HISLIP", "1") != "0"
)
_SOCKET_AVAILABLE = (
    _ASSISTED_AVAILABLE and os.environ.get("PYVISA_TESTER_SOCKET", "1") != "0"
)
_USB_AVAILABLE = _ASSISTED_AVAILABLE and os.environ.get("PYVISA_TESTER_USB", "1") != "0"

_BACKEND_SETTING = os.environ.get("PYVISA_LIBRARY", "")
_IS_PY_BACKEND = _BACKEND_SETTING == "@py"

require_pyvisa_tester_assisted = pytest.mark.skipif(
    not _ASSISTED_AVAILABLE,
    reason=("Requires pyvisa-tester-assisted endpoints. Set PYVISA_TESTER_ASSISTED=1."),
)

require_transport_vxi11 = pytest.mark.skipif(
    not _VXI11_AVAILABLE,
    reason="Requires VXI-11 endpoint via PYVISA_TESTER_VXI11_ADDR or PYVISA_TESTER_VXI11=1.",
)

require_transport_hislip = pytest.mark.skipif(
    not _HISLIP_AVAILABLE,
    reason="Requires HiSLIP endpoint via PYVISA_TESTER_HISLIP_ADDR or PYVISA_TESTER_HISLIP=1.",
)

require_transport_socket = pytest.mark.skipif(
    not _SOCKET_AVAILABLE,
    reason="Requires socket endpoint via PYVISA_TESTER_SOCKET_ADDR or PYVISA_TESTER_SOCKET=1.",
)

require_transport_usb = pytest.mark.skipif(
    not _USB_AVAILABLE,
    reason="Requires USB assisted mock enabled (PYVISA_TESTER_USB!=0).",
)

require_backend_py = pytest.mark.skipif(
    not _IS_PY_BACKEND,
    reason="Requires PYVISA_LIBRARY=@py (pyvisa-py backend).",
)

RESOURCE_ADDRESSES = {
    "TCPIP::INSTR": os.environ.get(
        "PYVISA_TESTER_VXI11_ADDR", "TCPIP::127.0.0.1::inst0::INSTR"
    ),
    "TCPIP::HISLIP": os.environ.get(
        "PYVISA_TESTER_HISLIP_ADDR", "TCPIP::127.0.0.1::hislip0::INSTR"
    ),
    "TCPIP::SOCKET": os.environ.get(
        "PYVISA_TESTER_SOCKET_ADDR", "TCPIP::127.0.0.1::5025::SOCKET"
    ),
    "USB::INSTR": os.environ.get(
        "PYVISA_TESTER_USB_INSTR_ADDR", "USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR"
    ),
}

EXPECTED_IDN = os.environ.get(
    "PYVISA_TESTER_EXPECTED_IDN", "Cyberdyne systems,T800 Model 101,A9012.C,V2.4"
)


# Even a deepcopy is not a true copy of a function.
def copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)."""
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = functools.update_wrapper(g, f)
    kwdefaults = getattr(f, "__kwdefaults__", None)
    if kwdefaults is not None:
        setattr(g, "__kwdefaults__", kwdefaults)
    return g
