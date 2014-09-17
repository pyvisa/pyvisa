# -*- coding: utf-8 -*-
"""
    pyvisa.resources.pxi
    ~~~~~~~~~~~~~~~~~~~~

    High level wrapper for pxi resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .. import constants

from .resource import Resource
from .registerbased import RegisterBasedResource


@Resource.register(constants.InterfaceType.pxi, 'INSTR')
class PXIInstrument(RegisterBasedResource):
    """Communicates with to devices of type PXI::<device>[::INSTR]

    More complex resource names can be specified with the following grammar:
        PXI[bus]::device[::function][::INSTR]
    or:
        PXI[interface]::bus-device[.function][::INSTR]
    or:
        PXI[interface]::CHASSISchassis number::SLOTslot number[::FUNCfunction][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """


@Resource.register(constants.InterfaceType.pxi, 'MEMACC')
class PXIMemory(RegisterBasedResource):
    """Communicates with to devices of type PXI[interface]::MEMACC

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """
