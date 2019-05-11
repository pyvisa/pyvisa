# -*- coding: utf-8 -*-
"""
    pyvisa.resources.tcpip
    ~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for TCPIP resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .. import constants

from .resource import Resource
from .messagebased import MessageBasedResource, ControlRenMixin


@Resource.register(constants.InterfaceType.tcpip, 'INSTR')
class TCPIPInstrument(ControlRenMixin, MessageBasedResource):
    """Communicates with to devices of type TCPIP::host address[::INSTR]

    More complex resource names can be specified with the following grammar:
        TCPIP[board]::host address[::LAN device name][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """
    pass


@Resource.register(constants.InterfaceType.tcpip, 'SOCKET')
class TCPIPSocket(MessageBasedResource):
    """Communicates with to devices of type TCPIP::host address::port::SOCKET

    More complex resource names can be specified with the following grammar:
        TCPIP[board]::host address::port::SOCKET

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """
    pass
