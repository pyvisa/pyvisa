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
from . import helpers as hlp

from .messagebased import MessageBasedResource

@MessageBasedResource.register(constants.InterfaceType.asrl, 'INSTR')
class SerialInstrument(MessageBasedResource):
    """Communicates with devices of type ASRL<board>[::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    _d_ = 'Controls transmission when inx XON/XOFF flow control.\n\n' \
          '- False: suspends transmission as if an XOFF character has been received.\n' \
          '- True: resumes transmission as if an XON character has been received.\n\n' \
          'Default is True.\n' \
          'If XON/XOFF flow control (software handshaking) is not being used, ' \
          'it is invalid to set this attribute to VI_FALSE.'
    allow_transmit = hlp.boolean_attr('VI_ATTR_ASRL_ALLOW_TRANSMIT', doc=_d_)

    bytes_in_buffer = hlp.range_attr('VI_ATTR_ASRL_AVAIL_NUM', 0, 2**32-1,
                                     doc='Number of bytes available in the low-level I/O receive buffer.',
                                     ro=True)

    baud_rate = hlp.range_attr('VI_ATTR_ASRL_BAUD', 1, 2**32-1,
                               'The baud rate of the serial instrument.\n\nDefault is 9600')

    break_length = hlp.range_attr('VI_ATTR_ASRL_BREAK_LEN', 1, 500,
                                  'The duration in milliseconds of the break signal.\n\nDefault is 250')

    break_state = hlp.enum_attr('VI_ATTR_ASRL_BREAK_STATE', constants.LineState,
                                'State of the break signal')

    data_bits = hlp.range_attr('VI_ATTR_ASRL_DATA_BITS', 5, 8,
                               'Number of data bits contained in each frame.\n\nDefault is 8')

    discard_null = hlp.boolean_attr('VI_ATTR_ASRL_DISCARD_NULL',
                                    'Specifies if NULL chars are discarded for transfers.\n\nDefault is False')

    stop_bits = hlp.enum_attr('VI_ATTR_ASRL_STOP_BITS', constants.StopBits,
                              'Number of stop bits contained in each frame.')

    parity = hlp.enum_attr('VI_ATTR_ASRL_PARITY', constants.Parity,
                           'The parity used with every frame transmitted and received.')

    end_input = hlp.enum_attr('VI_ATTR_ASRL_END_IN', constants.SerialTermination,
                              'Indicates the method used to terminate read operations.')

    replace_char = hlp.char_attr('VI_ATTR_ASRL_REPLACE_CHAR',
                                 'Specifies the character to be used to replace incoming characters '
                                 'that arrive with errors (such as parity error). Default is 0')

    xon_char = hlp.char_attr('VI_ATTR_ASRL_XON_CHAR',
                             'Specifies the value of the XON character used for XON/XOFF flow '
                             'control (both directions). Default is <Control-Q> (11h)')

    xoff_char = hlp.char_attr('VI_ATTR_ASRL_XOFF_CHAR',
                              'Specifies the value of the XOFF character used for XON/XOFF flow '
                              'control (both directions). Default is <Control-S> (13h)')

    del _d_

    def flush(self, mask):
        """Manually clears the specified buffers and cause the buffer data
        to be written to the device.

        :param mask: Specifies the action to be taken with flushing the buffer.
                 (Constants.READ*, .WRITE*, .IO*)
        """
        self.visalib.flush(mask)
