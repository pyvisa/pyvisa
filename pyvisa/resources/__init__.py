# -*- coding: utf-8 -*-
"""
    pyvisa.resources
    ~~~~~~~~~~~~~~~~

    High level wrappers for resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .resource import Resource

from .gpib import GPIBInterface
from .vxi import VXIBackplane
from .vxi import VXIInstrument

from .messagebased import MessageBasedResource
from .gpib import GPIBInstrument
from .tcpip import TCPIPInstrument
from .tcpip import TCPIPSocket
from .serial import SerialInstrument
from .usb import USBRaw
from .usb import USBInstrument

from .registerbased import RegisterBasedResource
from .firewire import FirewireInstrument
from .pxi import PXIMemory
from .pxi import PXIInstrument
from .vxi import VXIMemory

__all__ = ['Resource', 'MessageBasedResource', 'RegisterBasedResource',
           'GPIBInterface', 'VXIBackplane', 'VXIInstrument',
           'GPIBInstrument', 'TCPIPInstrument', 'TCPIPSocket', 'SerialInstrument', 'USBRaw', 'USBInstrument',
           'FirewireInstrument', 'PXIMemory', 'PXIInstrument', 'VXIMemory']
