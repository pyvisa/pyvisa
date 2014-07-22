# -*- coding: utf-8 -*-
"""
    pyvisa.resources.vxi
    ~~~~~~~~~~~~~~~~~~~~

    High level wrapper for VXI resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .. import constants

from .resource import Resource
from .registerbased import RegisterBasedResource


@Resource.register(constants.InterfaceType.firewire, 'INSTR')
class FirewireInstrument(Resource):
    """Communicates with to devices of type VXI::VXI logical address[::INSTR]

    More complex resource names can be specified with the following grammar:
        VXI[board]::VXI logical address[::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open`.

    :param resource_manager: A resource manager instance.
    :param resource_name: the VISA name for the resource.
    """
