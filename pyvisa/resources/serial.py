# -*- coding: utf-8 -*-
"""
    pyvisa.resources.serial
    ~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for Serial resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time
import warnings
import contextlib
from enum import IntEnum

from .. import logger
from ..constants import *
from .. import errors
from ..util import (warning_context, split_kwargs, warn_for_invalid_kwargs,
                    parse_ascii, parse_binary)

from .messagebased import MessageBasedResource
from .helpers import range_property

# The following aliases are used for the "end_input" property
no_end_input = VI_ASRL_END_NONE
last_bit_end_input = VI_ASRL_END_LAST_BIT
term_chars_end_input = VI_ASRL_END_TERMCHAR

# The following aliases are used for the "parity" property
no_parity = VI_ASRL_PAR_NONE
odd_parity = VI_ASRL_PAR_ODD
even_parity = VI_ASRL_PAR_EVEN
mark_parity = VI_ASRL_PAR_MARK
space_parity = VI_ASRL_PAR_SPACE


class SerialResource(MessageBasedResource):
    """Class for serial (RS232 or parallel port) resources. Not USB!

    This class extents the MessageBasedResource class with special operations and
    properties of serial instruments.

    :param resource_name: the instrument's resource name or an alias, may be
        taken from the list from `list_resources` method from a ResourceManager.

    Further keyword arguments are passed to the constructor of class
    Instrument.
    """

    DEFAULT_KWARGS = {'baud_rate': 9600,
                      'data_bits': 8,
                      'stop_bits': 1,
                      'parity': no_parity,
                      'end_input': term_chars_end_input}

    def __init__(self, resource_name, resource_manager=None, **keyw):
        skwargs, pkwargs = split_kwargs(keyw,
                                        SerialInstrument.DEFAULT_KWARGS.keys(),
                                        MessageBasedInstrument.ALL_KWARGS.keys())

        pkwargs.setdefault("read_termination", CR)
        pkwargs.setdefault("write_termination", CR)

        super(SerialInstrument, self).__init__(resource_name, resource_manager, **pkwargs)
        # Now check whether the instrument is really valid
        if self.interface_type != VI_INTF_ASRL:
            raise ValueError("device is not a serial instrument")

        for key, value in SerialInstrument.DEFAULT_KWARGS.items():
            setattr(self, key, skwargs.get(key, value))

    allow_transmit = boolean_property(VI_ATTR_ASRL_ALLOW_TRANSMIT,
                                      'If set to False, it suspends transmission as if an XOFF character '
                                      'has been received. '
                                      'If set to True, it resumes transmission as if an XON character has '
                                      'been received. Default is True ')

    @property
    def bytes_in_buffer(self):
        """Number of bytes available in the low-level I/O receive buffer.
        """
        return self.get_visa_attribute(VI_ATTR_ASRL_AVAIL_NUM)

    baud_rate = range_property(VI_ATTR_ASRL_BAUD, 1, 2**32-1,
                               'The baud rate of the serial instrument. Default is 9600')

    break_length = range_property(VI_ATTR_ASRL_BREAK_LEN, 1, 500,
                                  'The duration in milliseconds of the break signal. Default is 250')

    break_state = enum_property(VI_ATTR_ASRL_BREAK_STATE, constants.LineState,
                                'State of the break signal')

    data_bits = range_property(VI_ATTR_ASRL_DATA_BITS, 5, 8,
                               'Number of data bits contained in each frame. Default is 8')

    discard_null = boolean_property(VI_ATTR_ASRL_DISCARD_NULL,
                                    'Specifies if NULL chars are discarded for transfers. Default is False')

    @property
    def stop_bits(self):
        """Number of stop bits contained in each frame (1, 1.5, or 2).
        """

        deci_bits = self.get_visa_attribute(VI_ATTR_ASRL_STOP_BITS)
        if deci_bits == 10:
            return 1
        elif deci_bits == 15:
            return 1.5
        elif deci_bits == 20:
            return 2

    @stop_bits.setter
    def stop_bits(self, bits):
        deci_bits = 10 * bits
        if 9 < deci_bits < 11:
            deci_bits = 10
        elif 14 < deci_bits < 16:
            deci_bits = 15
        elif 19 < deci_bits < 21:
            deci_bits = 20
        else:
            raise ValueError("invalid number of stop bits")

        self.set_visa_attribute(VI_ATTR_ASRL_STOP_BITS, deci_bits)

    @property
    def parity(self):
        """The parity used with every frame transmitted and received."""

        return self.get_visa_attribute(VI_ATTR_ASRL_PARITY)

    @parity.setter
    def parity(self, parity):

        self.set_visa_attribute(VI_ATTR_ASRL_PARITY, parity)

    @property
    def end_input(self):
        """indicates the method used to terminate read operations"""

        return self.get_visa_attribute(VI_ATTR_ASRL_END_IN)

    @end_input.setter
    def end_input(self, termination):
        self.set_visa_attribute(VI_ATTR_ASRL_END_IN, termination)

    replace_char = char_property(VI_ATTR_ASRL_REPLACE_CHAR,
                                 'Specifies the character to be used to replace incoming characters '
                                 'that arrive with errors (such as parity error). Default is 0')

    xon_char = char_property(VI_ATTR_ASRL_XON_CHAR,
                             'Specifies the value of the XON character used for XON/XOFF flow '
                             'control (both directions). Default is <Control-Q> (11h)')

    xoff_char = char_property(VI_ATTR_ASRL_XOFF_CHAR,
                              'Specifies the value of the XOFF character used for XON/XOFF flow '
                              'control (both directions). Default is <Control-S> (13h)')

    def flush(self, mask):
        """Manually clears the specified buffers and cause the buffer data
        to be written to the device.

        :param mask: Specifies the action to be taken with flushing the buffer.
                 (Constants.READ*, .WRITE*, .IO*)
        """
        self._visalib.flush(mask)
