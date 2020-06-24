# -*- coding: utf-8 -*-
"""High level wrapper for Serial resources.

This file is part of PyVISA.

:copyright: 2014-2020 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
from .. import attributes, constants
from ..attributes import Attribute
from .messagebased import MessageBasedResource


@MessageBasedResource.register(constants.InterfaceType.asrl, "INSTR")
class SerialInstrument(MessageBasedResource):
    """Communicates with devices of type ASRL<board>[::INSTR]

    Do not instantiate directly, use
    :meth:`pyvisa.highlevel.ResourceManager.open_resource`.

    """

    #: Baud rate of the interface.
    baud_rate: Attribute[int] = attributes.AttrVI_ATTR_ASRL_BAUD()

    #: Number of data bits contained in each frame (from 5 to 8).
    data_bits: Attribute[int] = attributes.AttrVI_ATTR_ASRL_DATA_BITS()

    #: Parity used with every frame transmitted and received.
    parity: Attribute[constants.Parity] = attributes.AttrVI_ATTR_ASRL_PARITY()

    #: Number of stop bits used to indicate the end of a frame.
    stop_bits: Attribute[constants.StopBits] = attributes.AttrVI_ATTR_ASRL_STOP_BITS()

    #: Indicates the type of flow control used by the transfer mechanism.
    flow_control: Attribute[
        constants.ControlFlow
    ] = attributes.AttrVI_ATTR_ASRL_FLOW_CNTRL()

    #: Number of bytes available in the low- level I/O receive buffer.
    bytes_in_buffer: Attribute[int] = attributes.AttrVI_ATTR_ASRL_AVAIL_NUM()

    #: If set to True, NUL characters are discarded.
    discard_null: Attribute[bool] = attributes.AttrVI_ATTR_ASRL_DISCARD_NULL()

    #: Manually control transmission.
    allow_transmit: Attribute[bool] = attributes.AttrVI_ATTR_ASRL_ALLOW_TRANSMIT()

    #: Method used to terminate read operations.
    end_input: Attribute[
        constants.SerialTermination
    ] = attributes.AttrVI_ATTR_ASRL_END_IN()

    #: Method used to terminate write operations.
    end_output: Attribute[
        constants.SerialTermination
    ] = attributes.AttrVI_ATTR_ASRL_END_OUT()

    #: Duration (in milliseconds) of the break signal.
    break_length: Attribute[int] = attributes.AttrVI_ATTR_ASRL_BREAK_LEN()

    #: Manually control the assertion state of the break signal.
    break_state: Attribute[
        constants.LineState
    ] = attributes.AttrVI_ATTR_ASRL_BREAK_STATE()

    #: Character to be used to replace incoming characters that arrive with errors.
    replace_char: Attribute[str] = attributes.AttrVI_ATTR_ASRL_REPLACE_CHAR()

    #: XOFF character used for XON/XOFF flow control (both directions).
    xoff_char: Attribute[str] = attributes.AttrVI_ATTR_ASRL_XOFF_CHAR()

    #: XON character used for XON/XOFF flow control (both directions).
    xon_char: Attribute[str] = attributes.AttrVI_ATTR_ASRL_XON_CHAR()
