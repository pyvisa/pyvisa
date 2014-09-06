# -*- coding: utf-8 -*-
"""
    pyvisa.resources.serial
    ~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for Serial resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .. import constants

from .messagebased import MessageBasedResource

@MessageBasedResource.register(constants.InterfaceType.asrl, 'INSTR')
class SerialInstrument(MessageBasedResource):
    """Communicates with devices of type ASRL<board>[::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    def flush(self, mask):
        """Manually clears the specified buffers and cause the buffer data
        to be written to the device.

        :param mask: Specifies the action to be taken with flushing the buffer.
                 (Constants.READ*, .WRITE*, .IO*)
        """
        self.visalib.flush(mask)
