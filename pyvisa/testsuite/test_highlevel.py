# -*- coding: utf-8 -*-
"""Test highlevel functions not requiring an actual backend.

"""
import logging
import os
import sys

from pyvisa import highlevel, constants, rname
from pyvisa.ctwrapper import IVIVisaLibrary

from . import BaseTestCase


class TestHighlevel(BaseTestCase):
    """Test highlevel functionalities.

    """

    CHECK_NO_WARNING = False

    def test_base_class_parse_resource(self):
        """Test the base class implementation of parse_resource.

        """
        lib = highlevel.VisaLibraryBase()
        rsc_name = "TCPIP::192.168.0.1::INSTR"
        info, ret_code = lib.parse_resource(None, rsc_name)

        # interface_type interface_board_number resource_class resource_name alias
        for parsed, value in zip(
            info, (constants.InterfaceType.tcpip, 0, None, None, None)
        ):
            self.assertEqual(parsed, value)

        info, ret_code = lib.parse_resource_extended(None, rsc_name)
        # interface_type interface_board_number resource_class resource_name alias
        for parsed, value in zip(
            info,
            (
                constants.InterfaceType.tcpip,
                0,
                "INSTR",
                rname.to_canonical_name(rsc_name),
                None,
            ),
        ):
            self.assertEqual(parsed, value)

    def test_specifying_path_open_visa_library(self):
        """Test handling a specified path in open_visa_library.

        """
        with self.assertLogs(level=logging.DEBUG) as cm:
            with self.assertRaises(Exception) as e:
                highlevel.open_visa_library("non/existent/file")

        self.assertIn("Could not open VISA wrapper", cm.output[0])
        self.assertIn("non/existent/file", cm.output[0])

    def test_handling_error_in_opening_library(self):
        """Test handling errors when trying to open a Visa library.

        """

        class FakeLibrary(highlevel.VisaLibraryBase):
            @classmethod
            def get_library_paths(cls):
                return ["oserror", "error"]

            def _init(self):
                if self.library_path == "oserror":
                    raise OSError("oserror")
                else:
                    raise Exception("error")

        with self.assertLogs(level=logging.DEBUG) as cml:
            with self.assertRaises(OSError) as cm:
                FakeLibrary()

        self.assertIn("oserror", cml.output[0])

        msg = str(cm.exception).split("\n")
        self.assertEqual(len(msg), 3)
        self.assertIn("oserror", msg[1])
        self.assertIn("error", msg[2])

    def test_get_wrapper_class(self):
        """Test retrieving a wrapper class.

        """
        highlevel._WRAPPERS.clear()

        with self.assertWarns(FutureWarning):
            highlevel.get_wrapper_class("ni")
        self.assertIn("ivi", highlevel._WRAPPERS)

        path = os.path.join(os.path.dirname(__file__), "fake-extensions")
        sys.path.append(path)
        try:
            highlevel.get_wrapper_class("test")
        finally:
            sys.path.remove(path)

        self.assertIn("test", highlevel._WRAPPERS)

        with self.assertRaises(ValueError):
            highlevel.get_wrapper_class("dummy")

    def test_get_default_wrapper(self):
        """Test retrieving the default wrapper.

        """
        old_lib = IVIVisaLibrary.get_library_paths
        old_wrap = highlevel.get_wrapper_class

        def no_visa_found():
            return []

        def visa_found():
            return [""]

        def py_wrapper_class(backend):
            return True

        def no_py_wrapper_class(backend):
            raise ValueError()

        try:
            # No implementation found
            IVIVisaLibrary.get_library_paths = staticmethod(no_visa_found)
            highlevel.get_wrapper_class = no_py_wrapper_class

            with self.assertRaises(ValueError) as exc:
                with self.assertLogs(level=logging.DEBUG) as log:
                    highlevel._get_default_wrapper()

            self.assertIn("VISA implementation", exc.exception.args[0])
            self.assertIn("IVI binary", log.output[0])
            self.assertIn("find pyvisa-py", log.output[1])

            # Pyvisa-py found
            highlevel.get_wrapper_class = py_wrapper_class

            with self.assertLogs(level=logging.DEBUG) as log:
                self.assertEqual(highlevel._get_default_wrapper(), "py")

            self.assertIn("IVI binary", log.output[0])
            self.assertIn("pyvisa-py is available", log.output[1])

            # IVI visa found
            IVIVisaLibrary.get_library_paths = staticmethod(visa_found)

            with self.assertLogs(level=logging.DEBUG) as log:
                self.assertEqual(highlevel._get_default_wrapper(), "ivi")

            self.assertIn("IVI implementation available", log.output[0])

        finally:
            IVIVisaLibrary.get_library_paths = old_lib
            highlevel.get_wrapper_class = no_py_wrapper_class = old_wrap

    def test_register_resource_class(self):
        """Test registering resource classes.

        """
        old = highlevel.ResourceManager._resource_classes.copy()
        try:
            with self.assertLogs(level=logging.WARNING):
                highlevel.ResourceManager.register_resource_class(
                    constants.InterfaceType.tcpip, "INSTR", object
                )
            self.assertIs(
                highlevel.ResourceManager._resource_classes[
                    (constants.InterfaceType.tcpip, "INSTR")
                ],
                object,
            )
        finally:
            highlevel.ResourceManager._resource_classes = old

    def test_base_get_library_paths(self):
        """Test the base class implementation of get_library_paths.

        """
        self.assertEqual(("unset",), highlevel.VisaLibraryBase.get_library_paths())

    def test_base_get_debug_info(self):
        """Test the base class implementation of get_debug_info.

        """
        self.assertEqual(len(highlevel.VisaLibraryBase.get_debug_info()), 1)
