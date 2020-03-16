# -*- coding: utf-8 -*-
"""Test the behavior of the command line tools.

"""
from subprocess import run, Popen, PIPE

from pyvisa import util
from pyvisa.cmd_line_tools import visa_main, visa_info, visa_shell
from . import BaseTestCase, require_visa_lib


class TestCmdLineTools(BaseTestCase):
    """Test the cmd line tools functions and scripts.

    """

    @require_visa_lib
    def test_visa_main(self):
        """Test the visa scripts.

        The script is deprecated and will be removed, when it does this
        should be removed too.

        """
        result = run(
            ["python", "-m", "visa", "info"], stdout=PIPE, universal_newlines=True
        )
        details = util.system_details_to_str(util.get_system_details())
        self.assertSequenceEqual(result.stdout.strip(), details.strip())

        with Popen(["python", "-m", "visa", "shell"], stdin=PIPE, stdout=PIPE) as p:
            stdout, _ = p.communicate(b"exit")
        self.assertIn(b"Welcome to the VISA shell", stdout)

    def test_visa_info(self):
        """Test the visa info command line tool.

        """
        result = run("pyvisa-info", stdout=PIPE, universal_newlines=True)
        details = util.system_details_to_str(util.get_system_details())
        self.assertMultiLineEqual(result.stdout.strip(), details.strip())

    # XXX test backend selection: this not easy at all to assert
    @require_visa_lib
    def test_visa_shell(self):
        """Test the visa shell function.

        """
        with Popen(["pyvisa-shell"], stdin=PIPE, stdout=PIPE) as p:
            stdout, stderr = p.communicate(b"exit")
        self.assertIn(b"Welcome to the VISA shell", stdout)
