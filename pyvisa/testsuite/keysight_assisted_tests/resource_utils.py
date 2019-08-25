# -*- coding: utf-8 -*-
"""Common test case for all resources.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import unittest

from pyvisa import ResourceManager, InvalidSession, VisaIOError
from pyvisa.constants import (StatusCode, VI_ATTR_TMO_VALUE,
                              VI_TMO_IMMEDIATE, VI_TMO_INFINITE)
from pyvisa.rname import ResourceName

from . import RESOURCE_ADDRESSES


class ResourceTestCase(unittest.TestCase):
    """Base test case for all resources.

    """

    #: Type of resource being tested in this test case.
    #: See RESOURCE_ADDRESSES in the __init__.py file of this package for
    #: acceptable values
    RESOURCE_TYPE = ''

    def setup(self):
        """Create a resource using the address matching the type.

        """
        name = RESOURCE_ADDRESSES[self.RESOURCE_TYPE]
        self.rname = ResourceName.from_string(name)
        self.rm = ResourceManager()
        self.instr = self.rm.open_resource(name)

    def teardown(self):
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
        self.assertIsNone(self.instr.visalib)

        with self.rm.open_resource(str(self.rname)):
            self.assertEqual(len(self.rm.list_opened_resources()), 1)
        self.assertEqual(len(self.rm.list_opened_resources()), 0)

    def test_str(self):
        """Test the string representation of a resource.

        """
        self.assertRegex(str(self.instr), r".* at %s" % self.rname)
        self.instr.close()
        self.assertRegex(str(self.instr), r".* at %s" % self.rname)

    def test_repr(self):
        """Test the repr of a resource.

        """
        self.assertRegex(repr(self.instr), r"<.*\(%s\)>" % self.rname)
        self.instr.close()
        self.assertRegex(repr(self.instr), r"<.*\(%s\)>" % self.rname)

    def test_timeout(self):
        """Test setting the timeout attribute.

        """
        self.instr.timeout = None
        self.assertEqual(self.instr.timeout, float("+inf"))
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_INFINITE)

        self.instr.timeout = 0.1
        self.assertEqual(self.instr.timeout, 0)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_IMMEDIATE)

        self.instr.timeout = 10
        self.assertEqual(self.instr.timeout, 10)
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         10)

        with self.raises(ValueError):
            self.instr.timeout = 10000000000

        del self.timeout
        self.assertEqual(self.instr.timeout, float("+inf"))
        self.assertEqual(self.instr.get_visa_attribute(VI_ATTR_TMO_VALUE),
                         VI_TMO_INFINITE)

    def test_resource_info(self):
        """Test accessing the resource info.

        """
        rinfo = self.instr.resource_info
        self.assertEqual(rinfo.interface_type, rname.interface_type)
        self.assertEqual(rinfo.interface_board_number, rname.board)
        self.assertEqual(rinfo.resource_class, rname.resource_class)
        self.assertEqual(rinfo.resource_name, str(rname))

    def test_interface_type(self):
        """Test accessing the resource interface_type.

        """
        self.assertEqual(self.instr.interface_type, rname.interface_type)

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
                         VI_TMO_IMMEDIATE)
        self.assertEqual(self.instr.timeout, 0)

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
        instr2 = self.rm.open_resource(str(self.rname))
        instr3 = self.rm.open_resource(str(self.rname))

        key = self.instr.lock()
        instr2.lock(key)

        self.instr.timeout = 1
        instr2.timeout = 10
        self.assertEqual(self.instr.timeout, 10)
        with self.assertRaises(VisaIOError):
            instr3.timeout = 20

        # Share the lock for a limited time
        with instr3.lock_context(requested_key) as key2:
            self.assertEqual(key, key2)
            instr3.timeout = 20
        self.assertEqual(self.instr.timeout, 20)

        # Stop sharing the lock
        instr2.unlock()

        self.instr.timeout = 2
        self.assertEqual(self.instr.timeout, 2)
        with self.assertRaises(VisaIOError):
            instr2.timeout = 20
        with self.assertRaises(VisaIOError):
            instr3.timeout = 20

        self.instr.unlock()

        instr3.timeout = 30
        self.assertEqual(self.instr.timeout, 30)

    def test_exclusive_locking(self):
        """Test locking/unlocking a resource.

        """
        instr2 = self.rm.open_resource(str(self.rname))

        self.instr.lock_excl()
        with self.assertRaises(VisaIOError):
            instr2.timeout = 20

        self.instr.unlock()

        instr2.timeout = 30
        self.assertEqual(self.instr.timeout, 30)
