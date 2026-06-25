# -*- coding: utf-8 -*-
"""Test TCPIP resources against pyvisa-tester assisted fake instruments."""

import pytest

from pyvisa import VisaIOError, constants
from pyvisa.constants import ResourceAttribute
from pyvisa.testing.requirements import require_visa_lib

from .. import BaseTestCase
from . import EXPECTED_IDN

pytestmark = [
    require_visa_lib,
    pytest.mark.usefixtures("require_pyvisa_tester_profile"),
    pytest.mark.pyvisa_tester_assisted,
]


class AssistedResourceTestCase(BaseTestCase):
    """Base class for pyvisa-tester-assisted tests."""

    RESOURCE_TYPE = ""
    READ_TERMINATION = ""
    WRITE_TERMINATION = ""

    @pytest.fixture(autouse=True)
    def _assisted_instrument(self, require_assisted_resource, require_assisted_command):
        super().setup_method()
        self.rm = None
        self.instr = None
        self._expected_idn = ""
        self._identity_query = require_assisted_command("identity_query")
        self._shared_query = require_assisted_command("shared_query")

        from pyvisa import ResourceManager

        try:
            resource_name = require_assisted_resource(self.RESOURCE_TYPE)
            self.rm = ResourceManager()
            self.instr = self.rm.open_resource(resource_name)
            self.instr.read_termination = self.READ_TERMINATION
            self.instr.write_termination = self.WRITE_TERMINATION
            self.instr.timeout = 1000
            yield
        finally:
            if self.instr:
                self.instr.close()
            if self.rm:
                self.rm.close()
            super().teardown_method()

    def test_open_close(self):
        assert self.instr.session is not None

    def test_idn(self):
        expected_idn = self._expected_idn or EXPECTED_IDN
        assert self.instr.query(self._identity_query).strip() == expected_idn

    def test_query(self):
        assert self.instr.query(self._shared_query).strip() == "RESPONSE"

    def test_tcpip_attributes_readable(self):
        addr = self.instr.get_visa_attribute(ResourceAttribute.tcpip_address)
        assert isinstance(addr, str)
        assert addr


class TestTCPIPInstrVXI11(AssistedResourceTestCase):
    """Test VXI-11 based TCPIP INSTR resources."""

    RESOURCE_TYPE = "TCPIP::INSTR"

    @pytest.fixture(autouse=True)
    def _expected_profile_idn(self, require_pyvisa_profile):
        self._expected_idn = require_pyvisa_profile.expected_idn

    def test_read_stb(self):
        assert self.instr.read_stb() == 0

    def test_trigger_and_clear(self):
        self.instr.assert_trigger()
        assert self.instr.read_stb() & 0x40 != 0

        self.instr.clear()
        assert self.instr.read_stb() & 0x40 == 0

    def test_exclusive_lock(self):
        other = self.rm.open_resource(self.instr.resource_name)
        try:
            self.instr.lock_excl()
            with pytest.raises(VisaIOError):
                other.lock_excl(timeout=100)
            self.instr.unlock()
            other.lock_excl(timeout=1000)
            other.unlock()
        finally:
            other.close()


class TestTCPIPInstrHiSLIP(AssistedResourceTestCase):
    """Test HiSLIP based TCPIP INSTR resources."""

    RESOURCE_TYPE = "TCPIP::HISLIP"

    @pytest.fixture(autouse=True)
    def _expected_profile_idn(self, require_pyvisa_profile):
        self._expected_idn = require_pyvisa_profile.expected_idn

    def test_clear(self):
        self.instr.clear()

    def test_trigger(self):
        self.instr.assert_trigger()

    def test_exclusive_lock(self):
        self.instr.lock_excl(timeout=25000)
        self.instr.unlock()

    def test_shared_lock_timeout(self):
        second = self.rm.open_resource(self.instr.resource_name)
        third = self.rm.open_resource(self.instr.resource_name)
        try:
            self.instr.lock(requested_key="foo", timeout=0)
            second.lock(requested_key="foo", timeout=1000)
            with pytest.raises(VisaIOError):
                third.lock(requested_key="bar", timeout=1000)
            self.instr.unlock()
            second.unlock()
        finally:
            second.close()
            third.close()


class TestTCPIPSocket(AssistedResourceTestCase):
    """Test raw TCPIP SOCKET resources."""

    RESOURCE_TYPE = "TCPIP::SOCKET"
    READ_TERMINATION = "\n"
    WRITE_TERMINATION = "\n"

    @pytest.fixture(autouse=True)
    def _expected_profile_idn(self, require_pyvisa_profile):
        self._expected_idn = require_pyvisa_profile.expected_idn

    def test_socket_query(self):
        expected_idn = self._expected_idn or EXPECTED_IDN
        assert self.instr.query(self._identity_query).strip() == expected_idn

    def test_socket_port_attribute(self):
        port = self.instr.get_visa_attribute(ResourceAttribute.tcpip_port)
        assert isinstance(port, int)
        assert 0 < port <= 65535

    def test_socket_no_stb(self):
        with pytest.raises(VisaIOError):
            self.instr.read_stb()

    def test_nodelay_attr_roundtrip(self):
        original = self.instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay)
        self.instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, not original)
        assert self.instr.get_visa_attribute(ResourceAttribute.tcpip_nodelay) == (
            not original
        )
        self.instr.set_visa_attribute(ResourceAttribute.tcpip_nodelay, original)


def test_resource_class_resolution(require_assisted_resource):
    """Verify that configured resources open as expected classes."""
    from pyvisa import ResourceManager

    resource_name = require_assisted_resource("TCPIP::INSTR")
    rm = ResourceManager()
    try:
        instr = rm.open_resource(resource_name)
        try:
            assert instr.resource_class == "INSTR"
            assert instr.interface_type == constants.InterfaceType.tcpip
        finally:
            instr.close()
    finally:
        rm.close()
