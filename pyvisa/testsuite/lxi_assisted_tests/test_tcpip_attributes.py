# -*- coding: utf-8 -*-
"""TCPIP attribute checks against LXI fake instruments."""

import pytest

from pyvisa import ResourceManager
from pyvisa.constants import ResourceAttribute
from pyvisa.testsuite import require_visa_lib

from . import (
    RESOURCE_ADDRESSES,
    require_lxi_assisted,
    require_lxi_hislip,
    require_lxi_socket,
    require_lxi_vxi11,
)

pytestmark = [require_visa_lib]


@require_lxi_assisted
@require_lxi_vxi11
def test_vxi11_hostname_attr_is_string():
    rm = ResourceManager()
    instr = rm.open_resource(RESOURCE_ADDRESSES["TCPIP::INSTR"])
    try:
        hostname = instr.get_visa_attribute(ResourceAttribute.tcpip_hostname)
        assert isinstance(hostname, str)
    finally:
        instr.close()
        rm.close()


@require_lxi_assisted
@require_lxi_vxi11
def test_vxi11_nodelay_roundtrip():
    rm = ResourceManager()
    instr = rm.open_resource(RESOURCE_ADDRESSES["TCPIP::INSTR"])
    try:
        original = instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay)
        instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, not original)
        assert (
            instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay)
            == (not original)
        )
        instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, original)
    finally:
        instr.close()
        rm.close()


@require_lxi_assisted
@require_lxi_hislip
def test_hislip_is_hislip_attr():
    rm = ResourceManager()
    if rm.visalib.library_path == "py":
        pytest.skip("pyvisa-py does not support HiSLIP")
    instr = rm.open_resource(RESOURCE_ADDRESSES["TCPIP::HISLIP"])
    try:
        is_hislip = instr.get_visa_attribute(ResourceAttribute.tcpip_is_hislip)
        assert isinstance(is_hislip, bool)
    finally:
        instr.close()
        rm.close()

@require_lxi_assisted
@require_lxi_hislip
def test_hislip_version_attr():
    rm = ResourceManager()
    if rm.visalib.library_path == "py":
        pytest.skip("pyvisa-py does not support HiSLIP")
    instr = rm.open_resource(RESOURCE_ADDRESSES["TCPIP::HISLIP"])
    try:
        version = instr.get_visa_attribute(ResourceAttribute.tcpip_hislip_version)
        assert isinstance(version, int)
        assert version >= 0
    finally:
        instr.close()
        rm.close()


@require_lxi_assisted
@require_lxi_socket
def test_socket_keepalive_roundtrip():
    rm = ResourceManager()
    instr = rm.open_resource(RESOURCE_ADDRESSES["TCPIP::SOCKET"])
    try:
        original = instr.get_visa_attribute(ResourceAttribute.tcpip_keepalive)
        instr.set_visa_attribute(ResourceAttribute.tcpip_keepalive, not original)
        assert (
            instr.get_visa_attribute(ResourceAttribute.tcpip_keepalive)
            == (not original)
        )
        instr.set_visa_attribute(ResourceAttribute.tcpip_keepalive, original)
    finally:
        instr.close()
        rm.close()
