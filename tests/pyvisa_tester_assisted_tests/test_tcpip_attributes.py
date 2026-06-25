# -*- coding: utf-8 -*-
"""TCPIP attribute checks against pyvisa-tester-assisted fake instruments."""

import pytest

from pyvisa import ResourceManager
from pyvisa.constants import ResourceAttribute
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.usefixtures("require_pyvisa_tester_profile"),
    pytest.mark.pyvisa_tester_assisted,
]


def _open_tcpip_resource(resource_name: str):
    rm = ResourceManager()
    instr = rm.open_resource(resource_name)
    return rm, instr


def test_vxi11_hostname_attr_is_string(require_assisted_resource):
    rm, instr = _open_tcpip_resource(require_assisted_resource("TCPIP::INSTR"))
    try:
        hostname = instr.get_visa_attribute(ResourceAttribute.tcpip_hostname)
        assert isinstance(hostname, str)
    finally:
        instr.close()
        rm.close()


def test_vxi11_nodelay_roundtrip(require_assisted_resource):
    rm, instr = _open_tcpip_resource(require_assisted_resource("TCPIP::INSTR"))
    try:
        original = instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay)
        instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, not original)
        assert instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay) == (
            not original
        )
        instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, original)
    finally:
        instr.close()
        rm.close()


def test_hislip_is_hislip_attr(require_assisted_resource):
    rm, instr = _open_tcpip_resource(require_assisted_resource("TCPIP::HISLIP"))
    try:
        is_hislip = instr.get_visa_attribute(ResourceAttribute.tcpip_is_hislip)
        assert isinstance(is_hislip, bool)
    finally:
        instr.close()
        rm.close()


def test_hislip_version_attr(require_assisted_resource):
    rm, instr = _open_tcpip_resource(require_assisted_resource("TCPIP::HISLIP"))
    try:
        version = instr.get_visa_attribute(ResourceAttribute.tcpip_hislip_version)
        assert isinstance(version, int)
        assert version >= 0
    finally:
        instr.close()
        rm.close()


def test_socket_keepalive_roundtrip(require_assisted_resource):
    rm, instr = _open_tcpip_resource(require_assisted_resource("TCPIP::SOCKET"))
    try:
        original = instr.get_visa_attribute(ResourceAttribute.tcpip_keepalive)
        instr.set_visa_attribute(ResourceAttribute.tcpip_keepalive, not original)
        assert instr.get_visa_attribute(ResourceAttribute.tcpip_keepalive) == (
            not original
        )
        instr.set_visa_attribute(ResourceAttribute.tcpip_keepalive, original)
    finally:
        instr.close()
        rm.close()
