# -*- coding: utf-8 -*-
"""Test the TCPIP based resources.

"""
import os
import unittest

from .messagebased_resource_utils import MessagebasedResourceTestCase

unittest.skipUnless("PYVISA_KEYSIGHT_VIRTUAL_INSTR" in os.environ,
                    "Requires the Keysight virtual instrument. Run on PyVISA "
                    "buildbot.")


class TCPIPInstrTestCase(MessagebasedResourceTestCase,
                         unittest.TestCase):
    """Test pyvisa against a TCPIP INSTR resource.

    """
    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = 'TCPIP::INSTR'


# class TCPIPSocket(MessagebasedResourceTestCase):
#     """Test pyvisa against a TCPIP SOCKET resource.

#     """
#     #: Type of resource being tested in this test case.
#     #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
#     #: acceptable values
#     RESOURCE_TYPE = 'TCPIP::SOCKET'
