# -*- coding: utf-8 -*-
"""Test the capabilities of the ResourceManager.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import unittest

from pyvisa import ResourceManager, InvalidSession, VisaIOError
from pyvisa.constants import StatusCode, AccessModes
from pyvisa.rname import ResourceName

from . import RESOURCE_ADDRESSES


class TestResourceManager(unittest.TestCase):
    """Test the pyvisa ResourceManager.

    """

    def setup():
        """Create a ResourceManager with the default backend library.

        """
        self.rm = ResourceManager()

    def teardown(self):
        """Close the ResourceManager.

        """
        self.rm.close()

    def test_lifecycle(self):
        """Test creation and closing of the resource manager.

        """
        self.assertIsNotNone(self.rm.session)
        self.assertIsNotNone(self.rm.visalib)
        self.assertIs(self.rm, self.rm.visalib.resource_manager)
        self.assertFalse(self.rm.list_opened_resources())

        self.rm.close()

        with self.assertRaises(InvalidSession)
            self.rm.session
        self.assertIsNone(self.rm.visalib)
        self.assertIsNone(self.rm, self.rm.visalib.resource_manager)

    def test_resource_manager_unicity(self):
        """Test the resource manager is unique per backend as expected.

        """
        new_rm = ResourceManager()
        self.assertIs(self.rm, new_rm)
        self.assertEqual(self.rm.session, new_rm.session)

    def test_str(self):
        """Test computing the string representation of the resource manager

        """
        self.assertRegex(str(self.rm), r"Resource Manager of .*")
        self.rm.close()
        self.assertEqual(str(self.rm), r"Resource Manager of None")

    def test_repr(self):
        """Test computing the repr of the resource manager

        """
        self.assertRegex(repr(self.rm), r"<ResourceManager\(.*\)")
        self.rm.close()
        self.assertEqual(repr(self.rm), r"<ResourceManager\(None\)")

    def test_last_status(self):
        """Test accessing the status of the last operation.

        """
        self.assertEqual(self.rm.last_status, StatusCode.success)

    def test_list_resource(self):
        """Test listing the available resources.

        """
        # Default settings
        self.assertSequenceEqual(self.rm.list_resources(),
                                 [str(ResourceName.from_string(v))
                                  for v in RESOURCE_ADDRESSES.values()
                                  if v.endswith("INSTR")])

        # All resources
        self.assertSequenceEqual(self.rm.list_resources("?*"),
                                 [str(ResourceName.from_string(v))
                                  for v in RESOURCE_ADDRESSES.values()])

    def test_accessing_resource_infos(self):
        """Test accessing resource infos.

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        rinfo_ext = self.rm.resource_info(rname)
        rinfo = self.rm.resource_info(rname, extended=False)

        # Currently this is all done within Python so both are identical and
        # we do not have access to the alias info...
        rname = ResourceName(rname)
        self.assertEqual(rinfo_ext.interface_type, rname.interface_type)
        self.assertEqual(rinfo_ext.interface_board_number, rname.board)
        self.assertEqual(rinfo_ext.resource_class, rname.resource_class)
        self.assertEqual(rinfo_ext.resource_name, str(rname))

        self.assertEqual(rinfo.interface_type, rname.interface_type)
        self.assertEqual(rinfo.interface_board_number, rname.board)
        self.assertEqual(rinfo.resource_class, rname.resource_class)
        self.assertEqual(rinfo.resource_name, str(rname))

    def test_opening_resource(self):
        """Test opening and closing resources.

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        rsc = self.rm.open_resource(rname,
                                   timeout=1234)

        # Check the resource is listed as opened and the attributes are right.
        self.assertIn(rsc, self.rm.list_opened_resources())
        self.assertEqual(rsc.timeout, 1234)

        # Close the rm to check that we close all resources.
        self.rm.close()

        self.assertFalse(self.rm.list_opened_resources())
        with self.assertRaises(InvalidSession):
            rsc.session

    def test_opening_resource_with_lock(self):
        """Test opening a locked resource

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        rsc = self.rm.open_resource(rname,
                                    access_mode=AccessModes.exclusive_lock)
        self.assertEqual(len(self.rm.list_opened_resources()), 1)

        # Timeout when accessing a locked resource
        with self.assertRaises(VisaIOError):
            self.rm.open_resource(rname,
                                  access_mode=AccessModes.exclusive_lock)
        self.assertEqual(len(self.rm.list_opened_resources()), 1)

        # Success to access an unlocked resource.
        rsc.unlock()
        rsc2 = self.rm.open_resource(rname,
                                     access_mode=AccessModes.exclusive_lock)
        self.assertEqual(len(self.rm.list_opened_resources()), 2)

    def test_opening_resource_unknown_resource_type(self):
        """Test opening a resource while requesting an unknown resource type

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        with self.assertRaises(TypeError):
            rsc = self.rm.open_resource(rname, resource_pyclass=object)

        self.assertEqual(len(self.rm.list_opened_resources()), 0)

    def test_opening_resource_unknown_attribute(self):
        """Test opening a resource and attempting to set an unknown attr.

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        with self.assertRaises(TypeError):
            rsc = self.rm.open_resource(rname, unknown_attribute=None)

        self.assertEqual(len(self.rm.list_opened_resources()), 0)

    def test_get_instrument(self):
        """Check that we get the expected deprecation warning.

        """
        rname = list(RESOURCE_ADDRESSES.values())[0]
        with self.assertWarns(FutureWarning):
            rsc = self.rm.get_instrument(rname)
