# -*- coding: utf-8 -*-
"""Test the TCPIP based resources.

"""
import os
import unittest

from pyvisa import constants, errors

from . import require_virtual_instr
from .messagebased_resource_utils import MessagebasedResourceTestCase


@require_virtual_instr
class TCPIPInstrTestCase(MessagebasedResourceTestCase, unittest.TestCase):
    """Test pyvisa against a TCPIP INSTR resource.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = "TCPIP::INSTR"

    #: Minimal timeout value accepted by the resource. When setting the timeout
    #: to VI_TMO_IMMEDIATE, Visa (Keysight at least) may actually use a
    #: different value depending on the values supported by the resource.
    MINIMAL_TIMEOUT = 1

    def test_io_prot_attr(self):
        """Test getting/setting the io prot attribute.

        We would need to spy on the transaction to ensure we are sending a
        string instead of using the lower level mechanism.

        """
        try:
            self.instr.read_stb()
            # XXX note sure what is the actual issue here
            with self.assertRaises(errors.VisaIOError):
                self.instr.set_visa_attribute(
                    constants.VI_ATTR_IO_PROT, constants.IOProtocol.hs488
                )
            # self.instr.read_stb()
            # self.assertEqual(
            #     self.instr.get_visa_attribute(constants.VI_ATTR_IO_PROT),
            #     constants.IOProtocol.hs488)
        finally:
            self.instr.set_visa_attribute(
                constants.VI_ATTR_IO_PROT, constants.IOProtocol.normal
            )


@require_virtual_instr
class TCPIPSocket(MessagebasedResourceTestCase):
    """Test pyvisa against a TCPIP SOCKET resource.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = "TCPIP::SOCKET"

    #: Minimal timeout value accepted by the resource. When setting the timeout
    #: to VI_TMO_IMMEDIATE, Visa (Keysight at least) may actually use a
    #: different value depending on the values supported by the resource.
    MINIMAL_TIMEOUT = 1
