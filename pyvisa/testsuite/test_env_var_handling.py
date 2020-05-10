# -*- coding: utf-8 -*-
"""Test the reading of env vars.

"""
import sys
from subprocess import PIPE, Popen

from . import BaseTestCase


class TestEnvVarHandling(BaseTestCase):
    """Test reading env vars"""

    def test_reading_wrap_handler(self):
        with Popen([sys.executable], stdin=PIPE, stdout=PIPE) as p:
            stdout, _ = p.communicate(
                b"from pyvisa import ctwrapper;print(ctwrapper.WRAP_HANDLER);exit()"
            )
        self.assertSequenceEqual(b"True", stdout.rstrip())

        with Popen(
            [sys.executable], stdin=PIPE, stdout=PIPE, env={"PYVISA_WRAP_HANDLER": "0"},
        ) as p:
            stdout, _ = p.communicate(
                b"from pyvisa import ctwrapper;print(ctwrapper.WRAP_HANDLER);exit()"
            )
        self.assertSequenceEqual(b"False", stdout.rstrip())
