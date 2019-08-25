# -*- coding: utf-8 -*-
"""This package is meant to run against a PyVISA builbot.

The PyVISA builbot is connected to a fake instrument implemented using the
Keysight Virtual Instrument IO Test software.

For this part of the testsuite to be run, you need to set the
PYVISA_KEYSIGHT_VIRTUAL_INSTR environment value.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os
import unittest


RESOURCE_ADDRESSES = {
    # "GPIB::INSTR": "GPIB::19::INSTR",
    # "USB::INSTR": "USB::",
    "TCPIP::INSTR": "TCPIP::127.0.0.1::INSTR",  # ie localhost
    # "TCPIP::SOCKET": "TCPIP::192.168.0.2::5025::SOCKET",
}
