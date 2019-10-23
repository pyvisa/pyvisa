# -*- coding: utf-8 -*-
"""Test the shell.

"""
import sys
# set the platform to darwin to test the autocompletion
platform = sys.platform
sys.platform = "darwin"

from pyvisa.shell import Cmd, VisaShell
sys.platform = platform

from .. import BaseTestCase


class TestVisaShell(BaseTestCase):
    """Test the VISA shell.

    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_list(self):
        """

        """
        pass

    def test_list_handle_error(self):
        """

        """
        pass

    def test_open_no_args(self):
        """

        """
        pass

    def test_open_by_number(self):
        """

        """
        pass

    def test_open_by_address(self):
        """

        """
        pass

    def test_open_handle_exception(self):
        """

        """
        pass

    def test_handle_double_open(self):
        """

        """
        pass

    def test_complete_open(self):
        """

        """
        pass

    def test_command_on_closed_resource(self):
        """

        """
        pass

    def test_close(self):
        """

        """
        pass

    def test_close_handle_error(self):
        """

        """
        pass

    def test_query(self):
        """

        """
        pass

    def test_query_handle_error(self):
        """

        """
        pass

    def test_read(self):
        """

        """
        pass

    def test_read_handle_error(self):
        """

        """
        pass

    def test_write(self):
        """

        """
        pass

    def test_write_handle_error(self):
        """

        """
        pass

    def test_timeout_get(self):
        """

        """
        pass

    def test_timeout_get_handle_error(self):
        """

        """
        pass

    def test_timeout_set(self):
        """

        """
        pass

    def test_timeout_set_handle_error(self):
        """

        """
        pass

    def test_attr_no_args(self):
        """

        """
        pass

    def test_attr_wrong_args(self):
        """

        """
        pass

    def test_attr_get_by_VI(self):
        """

        """
        pass

    def test_attr_get_by_VI_handle_error(self):
        """

        """
        pass

    def test_attr_get_by_name(self):
        """

        """
        pass

    def test_attr_get_by_name_handle_error(self):
        """

        """
        pass

    def test_attr_set_by_VI(self):
        """

        """
        pass

    def test_attr_set_by_VI_handle_error(self):
        """

        """
        pass

    def test_attr_set_by_name(self):
        """

        """
        pass

    def test_attr_set_by_name_handle_error(self):
        """

        """
        pass

    def test_complete_attr(self):
        """

        """
        pass

    def test_termchar_get(self):
        """

        """
        pass

    def test_termchar_get_handle_error(self):
        """

        """
        pass

    def test_termchar_set(self):
        """

        """
        pass

    def test_termchar_set_wrong_args(self):
        """

        """
        pass

    def test_termchar_set_handle_error(self):
        """

        """
        pass

    def test_exit(self):
        """

        """
        pass

