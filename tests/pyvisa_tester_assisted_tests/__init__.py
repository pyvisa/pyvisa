# -*- coding: utf-8 -*-
"""pyvisa-tester-assisted tests for multiple transports and backends."""

import functools
import types

import pytest

from .config import PYVISA_TESTER_EXPECTED_IDN, PYVISA_TESTER_RESOURCE_ADDRESSES

# Backward-compatible aliases for older assisted tests.
# New tests should use require_assisted_resource fixture from conftest.py.
require_pyvisa_tester_assisted = pytest.mark.usefixtures(
    "require_pyvisa_tester_profile"
)
require_transport_vxi11 = pytest.mark.usefixtures("require_pyvisa_tester_profile")
require_transport_hislip = pytest.mark.usefixtures("require_pyvisa_tester_profile")
require_transport_socket = pytest.mark.usefixtures("require_pyvisa_tester_profile")
require_transport_usb = pytest.mark.usefixtures("require_pyvisa_tester_profile")

RESOURCE_ADDRESSES = PYVISA_TESTER_RESOURCE_ADDRESSES
EXPECTED_IDN = PYVISA_TESTER_EXPECTED_IDN


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
