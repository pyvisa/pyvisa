# -*- coding: utf-8 -*-
"""Test the behavior of the command line tools.

"""
import sys
from subprocess import PIPE, Popen, run

import pytest

from pyvisa import util

from . import BaseTestCase, require_visa_lib


class TestCmdLineTools(BaseTestCase):
    """Test the cmd line tools functions and scripts."""

    def test_visa_main_argument_handling(self):
        """Test we reject invalid values in visa_main."""
        from pyvisa.cmd_line_tools import visa_main

        old = sys.argv = ["python"]
        try:
            with pytest.raises(ValueError):
                visa_main("unknown")
        finally:
            sys.argv = old

    def test_visa_info(self):
        """Test the visa info command line tool."""
        result = run("pyvisa-info", stdout=PIPE, universal_newlines=True)
        details = util.system_details_to_str(util.get_system_details())
        # Path difference can lead to subtle differences in the backends
        # and Python path so compare only the first lines.
        assert result.stdout.strip().split("\n")[:5] == details.strip().split("\n")[:5]

    # TODO test backend selection: this is not easy at all to assert
    @require_visa_lib
    def test_visa_shell(self):
        """Test the visa shell function."""
        with Popen(["pyvisa-shell"], stdin=PIPE, stdout=PIPE) as p:
            stdout, stderr = p.communicate(b"exit")
        assert stdout.count(b"Welcome to the VISA shell") == 1
