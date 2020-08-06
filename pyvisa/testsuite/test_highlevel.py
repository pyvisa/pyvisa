# -*- coding: utf-8 -*-
"""Test highlevel functions not requiring an actual backend.

"""
import logging
import os
import sys

import pytest

from pyvisa import constants, highlevel, resources, rname
from pyvisa.ctwrapper import IVIVisaLibrary

from . import BaseTestCase


class TestHighlevel(BaseTestCase):
    """Test highlevel functionalities.

    """

    CHECK_NO_WARNING = False

    def test_base_class_parse_resource(self):
        """Test the base class implementation of parse_resource.

        """
        lib = highlevel.VisaLibraryBase("test")
        rsc_name = "TCPIP::192.168.0.1::INSTR"
        info, ret_code = lib.parse_resource(None, rsc_name)

        # interface_type interface_board_number resource_class resource_name alias
        for parsed, value in zip(
            info, (constants.InterfaceType.tcpip, 0, None, None, None)
        ):
            assert parsed == value

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
            assert parsed == value

    def test_base_class_parse_resource_error(self):
        """Test errors in the base class implementation of parse_resource.

        """
        lib = highlevel.VisaLibraryBase("test")
        rsc_name = "UNKNOWN::1::INSTR"
        info, ret_code = lib.parse_resource(None, rsc_name)

        assert ret_code == constants.StatusCode.error_invalid_resource_name
        assert info[0] == constants.InterfaceType.unknown

    def test_specifying_path_open_visa_library(self, caplog):
        """Test handling a specified path in open_visa_library.

        """
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(Exception):
                highlevel.open_visa_library("non/existent/file")

        assert "Could not open VISA wrapper" in caplog.records[0].message
        assert "non/existent/file" in caplog.records[0].message

    def test_handling_error_in_opening_library(self, caplog):
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

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(OSError) as cm:
                FakeLibrary()

        assert "oserror" in caplog.records[0].message

        msg = str(cm.exconly()).split("\n")
        assert len(msg) == 3
        assert "oserror" in msg[1]
        assert "error" in msg[2]

    def test_get_wrapper_class(self):
        """Test retrieving a wrapper class.

        """
        highlevel._WRAPPERS.clear()

        with pytest.warns(FutureWarning):
            highlevel.get_wrapper_class("ni")
        assert "ivi" in highlevel._WRAPPERS

        path = os.path.join(os.path.dirname(__file__), "fake-extensions")
        sys.path.append(path)
        try:
            highlevel.get_wrapper_class("test")
        finally:
            sys.path.remove(path)

        assert "test" in highlevel._WRAPPERS

        with pytest.raises(ValueError):
            highlevel.get_wrapper_class("dummy")

    def test_get_default_wrapper(self, caplog):
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

            with pytest.raises(ValueError) as exc:
                with caplog.at_level(logging.DEBUG):
                    highlevel._get_default_wrapper()

            assert "VISA implementation" in exc.exconly()
            assert "IVI binary" in caplog.records[0].message
            assert "find pyvisa-py" in caplog.records[1].message

            caplog.clear()
            # Pyvisa-py found
            highlevel.get_wrapper_class = py_wrapper_class

            with caplog.at_level(logging.DEBUG):
                assert highlevel._get_default_wrapper() == "py"

            assert "IVI binary" in caplog.records[0].message
            assert "pyvisa-py is available" in caplog.records[1].message

            caplog.clear()
            # IVI visa found
            IVIVisaLibrary.get_library_paths = staticmethod(visa_found)

            with caplog.at_level(logging.DEBUG):
                assert highlevel._get_default_wrapper() == "ivi"

            assert "IVI implementation available" in caplog.records[0].message

        finally:
            IVIVisaLibrary.get_library_paths = old_lib
            highlevel.get_wrapper_class = no_py_wrapper_class = old_wrap

    def test_register_resource_class(self, caplog):
        """Test registering resource classes.

        """
        old = highlevel.ResourceManager._resource_classes.copy()
        try:

            class SubTCPIP(resources.TCPIPInstrument):
                pass

            with caplog.at_level(logging.WARNING):
                highlevel.ResourceManager.register_resource_class(
                    constants.InterfaceType.tcpip, "INSTR", SubTCPIP
                )

            assert caplog.records

            assert (
                highlevel.ResourceManager._resource_classes[
                    (constants.InterfaceType.tcpip, "INSTR")
                ]
                is SubTCPIP
            )
        finally:
            highlevel.ResourceManager._resource_classes = old

    def test_register_resource_class_missing_attr(self):
        """Test registering resource classes.

        """
        old = highlevel.ResourceManager._resource_classes.copy()
        try:
            with pytest.raises(TypeError):
                highlevel.ResourceManager.register_resource_class(
                    constants.InterfaceType.tcpip, "INSTR", object
                )
            assert (
                highlevel.ResourceManager._resource_classes[
                    (constants.InterfaceType.tcpip, "INSTR")
                ]
                is not object
            )
        finally:
            highlevel.ResourceManager._resource_classes = old

    def test_base_get_library_paths(self):
        """Test the base class implementation of get_library_paths.

        """
        assert () == highlevel.VisaLibraryBase.get_library_paths()

    def test_base_get_debug_info(self):
        """Test the base class implementation of get_debug_info.

        """
        assert len(highlevel.VisaLibraryBase.get_debug_info()) == 1
