# -*- coding: utf-8 -*-
"""Common test case for all resources.

"""
import unittest

from pyvisa import ResourceManager, InvalidSession, VisaIOError
from pyvisa.constants import (StatusCode, InterfaceType, VI_ATTR_TMO_VALUE,
                              VI_TMO_IMMEDIATE, VI_TMO_INFINITE)
from pyvisa.rname import ResourceName
from pyvisa.resources.resource import Resource

from . import RESOURCE_ADDRESSES


class ResourceTestCase:
    """Base test case for all resources.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = ''

    #: Minimal timeout value accepted by the resource. When setting the timeout
    #: to VI_TMO_IMMEDIATE, Visa (Keysight at least) may actually use a
    #: different value depending on the values supported by the resource.
    MINIMAL_TIMEOUT = VI_TMO_IMMEDIATE

    def setUp(self):
        """Create a resource using the address matching the type.

        """
        name = RESOURCE_ADDRESSES[self.RESOURCE_TYPE]
        self.rname = ResourceName.from_string(name)
        self.rm = ResourceManager()
        self.instr = self.rm.open_resource(name)
        self.instr.clear()

    def tearDown(self):
        """Close the resource at the end of the test.

        """
        self.instr.close()
        self.rm.close()

    def test_lifecycle(self):
        """Test the lifecyle of a resource and the use as a context manager.

        """
        self.assertIsNotNone(self.instr.session)
        self.assertIsNotNone(self.instr.visalib)
        self.assertEqual(self.instr.last_status, StatusCode.success)

        self.instr.close()

        with self.assertRaises(InvalidSession):
            self.instr.session

        with self.rm.open_resource(str(self.rname)) as instr:
            self.assertEqual(len(self.rm.list_opened_resources()), 1)
        self.assertEqual(len(self.rm.list_opened_resources()), 0)

    def test_alias_bypassing(self):
        """Test that a resource that cannot normalize an alias keep the alias.

        """
        instr = Resource(self.rm, "visa_alias")
        self.assertRegex(str(instr), r".* at %s" % "visa_alias")

    def test_str(self):
        """Test the string representation of a resource.

        """
        self.assertRegex(str(self.instr), r".* at %s" % str(self.rname))
        self.instr.close()
        self.assertRegex(str(self.instr), r".* at %s" % str(self.rname))

    def test_repr(self):
        """Test the repr of a resource.

        """
        self.assertRegex(repr(self.instr), r"<.*\('%s'\)>" % str(self.rname))
        self.instr.close()
        self.assertRegex(repr(self.instr), r"<.*\('%s'\)>" % str(self.rname))

    def test_timeout(self):
        """Test setting the timeout attribute.

        """
        self.instr.timeout = None
        self.assertEqual(self.instr.timeout, float("+inf"))
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_INFINITE)

        self.instr.timeout = 0.1
        self.assertEqual(self.instr.timeout, 1)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         self.MINIMAL_TIMEOUT)

        self.instr.timeout = 10
        self.assertEqual(self.instr.timeout, 10)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         10)

        with self.assertRaises(ValueError):
            self.instr.timeout = 10000000000

        del self.instr.timeout
        self.assertEqual(self.instr.timeout, float("+inf"))
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_INFINITE)

    def test_resource_info(self):
        """Test accessing the resource info.

        """
        rinfo, status = self.instr.resource_info
        self.assertEqual(rinfo.interface_type,
                         getattr(InterfaceType, self.rname.interface_type.lower()))
        self.assertEqual(rinfo.interface_board_number, int(self.rname.board))
        self.assertEqual(rinfo.resource_class, self.rname.resource_class)
        self.assertEqual(rinfo.resource_name, str(self.rname))

    def test_interface_type(self):
        """Test accessing the resource interface_type.

        """
        self.assertEqual(self.instr.interface_type,
                         getattr(InterfaceType, self.rname.interface_type.lower()))

    def test_attribute_handling(self):
        """Test directly manipulating attributes ie not using descriptors.

        This should extended in subclasses to test a broader range of
        attributes.

        """
        self.instr.set_visa_attribute(VI_ATTR_TMO_VALUE, 10)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE), 10)
        self.assertEqual(self.instr.timeout, 10)

        self.instr.set_visa_attribute(VI_ATTR_TMO_VALUE, VI_TMO_IMMEDIATE)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         self.MINIMAL_TIMEOUT)
        self.assertEqual(self.instr.timeout, 1)

        self.instr.set_visa_attribute(VI_ATTR_TMO_VALUE, VI_TMO_INFINITE)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_INFINITE)
        self.assertEqual(self.instr.timeout, float("+inf"))

    def test_wait_on_event(self):
        """Test waiting on a VISA event.

        Should be implemented on subclasses, since the way to generate the
        event may be dependent on the resource type.

        """
        raise NotImplementedError()

    def test_managing_visa_handler(self):
        """Test using visa handlers.

        Should be implemented on subclasses, since the way to generate the
        event may be dependent on the resource type.

        """
        raise NotImplementedError()

    def test_shared_locking(self):
        """Test locking/unlocking a resource.

        """
        raise NotImplementedError()

    def test_exclusive_locking(self):
        """Test locking/unlocking a resource.

        """
        raise NotImplementedError()
