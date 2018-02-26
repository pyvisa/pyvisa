# -*- coding: utf-8 -*-
"""
    pyvisa.attributes
    ~~~~~~~~~~~~~~~~~

    Comprehensive of all properties.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from collections import defaultdict

from .compat import with_metaclass
from . import constants

#: Not available value.
NotAvailable = object()

#: Attribute for all session types.
AllSessionTypes = object()


#: Map resource to attribute
AttributesPerResource = defaultdict(set)
AttributesByID = dict()


class AttributeType(type):
    """Base Type for Attributes

    Assigns the `attribute_id` and improves the documentation.
    """

    def __init__(cls, name, bases, dct):
        super(AttributeType, cls).__init__(name, bases, dct)
        if not name.startswith('AttrVI_'):
            return
        cls.attribute_id = getattr(constants, cls.visa_name)
        # Check that the docstring are populated before extending them
        # Cover the case of running with Python with -OO option
        if cls.__doc__ is not None:
            cls.redoc()
        if cls.resources is AllSessionTypes:
            AttributesPerResource[AllSessionTypes].add(cls)
        else:
            for res in cls.resources:
                AttributesPerResource[res].add(cls)
        AttributesByID[cls.attribute_id] = cls


class Attribute(with_metaclass(AttributeType)):
    """Base class for Attributes to be used as Properties.
    """

    #: List of resource types with this attribute.
    #: each element is a tuple (constants.InterfaceType, str)
    resources = []

    #: Name of the Python property to be matched to this attribute.
    py_name = 'To be specified'

    #: Name of the VISA Attribute
    visa_name = 'To be specified'

    #: Numeric constant of the VISA Attribute
    attribute_id = 0

    #: Default value fo the VISA Attribute
    default = 'N/A'

    #: Access
    read, write, local = False, False, False

    @classmethod
    def redoc(cls):
        cls.__doc__ += '\n:VISA Attribute: %s (%s)' % (cls.visa_name,
                                                       cls.attribute_id)

    def post_get(self, value):
        """Override this method to check or modify the value returned by the VISA function.

        :param value: the value returned by the VISA library.
        :return: the equivalent python value.
        """
        return value

    def pre_set(self, value):
        """Override this method to check or modify the value to be passed to the VISA function.

        :param value: the python value to be passed to VISA library.
        :return: the equivalent value.
        """
        return value

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not self.read:
            raise AttributeError("can't read attribute")

        return self.post_get(instance.get_visa_attribute(self.attribute_id))

    def __set__(self, instance, value):
        if not self.write:
            raise AttributeError("can't write attribute")

        instance.set_visa_attribute(self.attribute_id, self.pre_set(value))

    @classmethod
    def in_resource(cls, session_type):
        """Returns True if the attribute is part of a given session type.

        The session_type is a tuple with the interface type and resource_class

        :type session_type: (constants.InterfaceType, str)
        :rtype: bool
        """
        if cls.resources is AllSessionTypes:
            return True
        return session_type in cls.resources


class EnumAttribute(Attribute):
    """Class for attributes with values that map to a PyVISA Enum.
    """

    #: Enum type with valid values.
    enum_type = None

    @classmethod
    def redoc(cls):
        super(EnumAttribute, cls).redoc()
        cls.__doc__ += '\n:type: :class:%s.%s' % (cls.enum_type.__module__,
                                                  cls.enum_type.__name__)

    def post_get(self, value):
        return self.enum_type(value)

    def pre_set(self, value):
        if value not in self.enum_type:
            raise ValueError('%r is an invalid value for attribute %s, '
                             'should be a %r' % (value,
                                                 self.visa_name,
                                                 self.enum_type))
        return value


class IntAttribute(Attribute):
    """Class for attributes with integers values.
    """

    @classmethod
    def redoc(cls):
        super(IntAttribute, cls).redoc()
        cls.__doc__ += '\n:type: int'

    def post_get(self, value):
        return int(value)


class RangeAttribute(IntAttribute):
    """Class for integer attributes with values within a range.
    """

    #: Range for the value, and iterable of extra values.
    min_value, max_value, values = None, None, []

    @classmethod
    def redoc(cls):
        super(RangeAttribute, cls).redoc()
        cls.__doc__ += '\n:range: %s <= value <= %s' % (cls.min_value,
                                                        cls.max_value)
        if cls.values:
            cls.__doc__ += ' or in %s' % cls.values

    def pre_set(self, value):
        if not self.min_value <= value <= self.max_value:
            if not self.values:
                raise ValueError('%r is an invalid value for attribute %s, '
                                 'should be between %r and %r' % (
                                                            value,
                                                            self.visa_name,
                                                            self.min_value,
                                                            self.max_value))
            elif value not in self.values:
                raise ValueError('%r is an invalid value for attribute %s, '
                                 'should be between %r and %r or %r' % (
                                                            value,
                                                            self.visa_name,
                                                            self.min_value,
                                                            self.max_value,
                                                            self.values))
        return value


class ValuesAttribute(Attribute):
    """Class for attributes with values in a list.
    """

    #: Valid values
    values = []

    @classmethod
    def redoc(cls):
        super(ValuesAttribute, cls).redoc()
        cls.__doc__ += '\n:values: %s' % cls.values

    def pre_set(self, value):
        if value not in self.values:
            raise ValueError('%r is an invalid value for attribute %s, '
                             'should be in %s' % (value,
                                                  self.visa_name,
                                                  self.values))
        return value


class BooleanAttribute(Attribute):
    """Class for attributes with boolean values.
    """

    @classmethod
    def redoc(cls):
        super(BooleanAttribute, cls).redoc()
        cls.__doc__ += '\n:type: bool'

    def post_get(self, value):
        return value == constants.VI_TRUE

    def pre_set(self, value):
        return constants.VI_TRUE if value else constants.VI_FALSE


class CharAttribute(Attribute):
    """Class for attributes with char values.
    """

    @classmethod
    def redoc(cls):
        super(CharAttribute, cls).redoc()
        cls.__doc__ += '\n:range: 0 <= x <= 255\n:type: int'

    def post_get(self, value):
        return chr(value)

    def pre_set(self, value):
        return ord(value)


# noinspection PyPep8Naming
class AttrVI_ATTR_4882_COMPLIANT(BooleanAttribute):
    """VI_ATTR_4882_COMPLIANT specifies whether the device is 488.2
    compliant.
    """
    resources = [(constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = 'is_4882_compliant'

    visa_name = 'VI_ATTR_4882_COMPLIANT'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_ALLOW_TRANSMIT(BooleanAttribute):
    """If set to VI_FALSE, it suspends transmission as if an XOFF character
    has been received. If set to VI_TRUE, it resumes transmission as
    if an XON character has been received.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'allow_transmit'

    visa_name = 'VI_ATTR_ASRL_ALLOW_TRANSMIT'

    visa_type = 'ViBoolean'

    default = True

    read, write, local = True, True, False


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_AVAIL_NUM(RangeAttribute):
    """VI_ATTR_ASRL_AVAIL_NUM shows the number of bytes available in the low-
    level I/O receive buffer.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'bytes_in_buffer'

    visa_name = 'VI_ATTR_ASRL_AVAIL_NUM'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFFFFFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_BAUD(RangeAttribute):
    """VI_ATTR_ASRL_BAUD is the baud rate of the interface. It is represented
    as an unsigned 32-bit integer so that any baud rate can be used,
    but it usually requires a commonly used rate such as 300, 1200,
    2400, or 9600 baud.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'baud_rate'

    visa_name = 'VI_ATTR_ASRL_BAUD'

    visa_type = 'ViUInt32'

    default = 9600

    read, write, local = True, True, False

    min_value, max_value, values = 0, 0xFFFFFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_BREAK_LEN(RangeAttribute):
    """This controls the duration (in milliseconds) of the break signal
    asserted when VI_ATTR_ASRL_END_OUT is set to VI_ASRL_END_BREAK. If
    you want to control the assertion state and length of a break
    signal manually, use the VI_ATTR_ASRL_BREAK_STATE attribute
    instead.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'break_length'

    visa_name = 'VI_ATTR_ASRL_BREAK_LEN'

    visa_type = 'ViInt16'

    default = 250

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_BREAK_STATE(EnumAttribute):
    """If set to VI_STATE_ASSERTED, it suspends character transmission and
    places the transmission line in a break state until this attribute
    is reset to VI_STATE_UNASSERTED. This attribute lets you manually
    control the assertion state and length of a break signal. If you
    want VISA to send a break signal after each write operation
    automatically, use the VI_ATTR_ASRL_BREAK_LEN and
    VI_ATTR_ASRL_END_OUT attributes instead.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'break_state'

    visa_name = 'VI_ATTR_ASRL_BREAK_STATE'

    visa_type = 'ViInt16'

    default = constants.LineState.unasserted

    read, write, local = True, True, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_CONNECTED(BooleanAttribute):
    """VI_ATTR_ASRL_CONNECTED indicates whether the port is properly
    connected to another port or device. This attribute is valid only
    with serial drivers developed by National Instruments and
    documented to support this feature with the corresponding National
    Instruments hardware.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_CONNECTED'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_CTS_STATE(EnumAttribute):
    """VI_ATTR_ASRL_CTS_STATE shows the current state of the Clear To Send
    (CTS) input signal.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_CTS_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_DATA_BITS(RangeAttribute):
    """VI_ATTR_ASRL_DATA_BITS is the number of data bits contained in each
    frame (from 5 to 8). The data bits for each frame are located in
    the low-order bits of every byte stored in memory.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'data_bits'

    visa_name = 'VI_ATTR_ASRL_DATA_BITS'

    visa_type = 'ViUInt16'

    default = 8

    read, write, local = True, True, False

    min_value, max_value, values = 5, 8, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_DCD_STATE(EnumAttribute):
    """VI_ATTR_ASRL_DCD_STATE represents the current state of the Data
    Carrier Detect (DCD) input signal. The DCD signal is often used by
    modems to indicate the detection of a carrier (remote modem) on
    the telephone line. The DCD signal is also known as Receive Line
    Signal Detect (RLSD). This attribute is Read Only except when the
    VI_ATTR_ASRL_WIRE_MODE attribute is set to VI_ASRL_WIRE_232_DCE,
    or VI_ASRL_WIRE_232_AUTO with the hardware currently in the DCE
    state.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_DCD_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_DISCARD_NULL(BooleanAttribute):
    """If set to VI_TRUE, NUL characters are discarded. Otherwise, they are
    treated as normal data characters. For binary transfers, set this
    attribute to VI_FALSE.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'discard_null'

    visa_name = 'VI_ATTR_ASRL_DISCARD_NULL'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, False


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_DSR_STATE(EnumAttribute):
    """VI_ATTR_ASRL_DSR_STATE shows the current state of the Data Set Ready
    (DSR) input signal.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_DSR_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_DTR_STATE(EnumAttribute):
    """VI_ATTR_ASRL_DTR_STATE shows the current state of the Data Terminal
    Ready (DTR) input signal.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_DTR_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_END_IN(EnumAttribute):
    """VI_ATTR_ASRL_END_IN indicates the method used to terminate read
    operations.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'end_input'

    visa_name = 'VI_ATTR_ASRL_END_IN'

    visa_type = 'ViUInt16'

    default = constants.SerialTermination.termination_char

    read, write, local = True, True, True

    enum_type = constants.SerialTermination


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_END_OUT(EnumAttribute):
    """VI_ATTR_ASRL_END_OUT indicates the method used to terminate write
    operations.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_END_OUT'

    visa_type = 'ViUInt16'

    default = constants.SerialTermination.none

    read, write, local = True, True, True

    enum_type = constants.SerialTermination


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_FLOW_CNTRL(RangeAttribute):
    """VI_ATTR_ASRL_FLOW_CNTRL indicates the type of flow control used by the
    transfer mechanism.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'flow_control'

    visa_name = 'VI_ATTR_ASRL_FLOW_CNTRL'

    visa_type = 'ViUInt16'

    default = constants.VI_ASRL_FLOW_NONE

    read, write, local = True, True, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_PARITY(EnumAttribute):
    """VI_ATTR_ASRL_PARITY is the parity used with every frame transmitted
    and received.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'parity'

    visa_name = 'VI_ATTR_ASRL_PARITY'

    visa_type = 'ViUInt16'

    default = constants.Parity.none

    read, write, local = True, True, False

    enum_type = constants.Parity


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_REPLACE_CHAR(RangeAttribute):
    """VI_ATTR_ASRL_REPLACE_CHAR specifies the character to be used to
    replace incoming characters that arrive with errors (such as
    parity error).
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'replace_char'

    visa_name = 'VI_ATTR_ASRL_REPLACE_CHAR'

    visa_type = 'ViUInt8'

    default = 0

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_RI_STATE(EnumAttribute):
    """VI_ATTR_ASRL_RI_STATE represents the current state of the Ring
    Indicator (RI) input signal. The RI signal is often used by modems
    to indicate that the telephone line is ringing. This attribute is
    Read Only except when the VI_ATTR_ASRL_WIRE_MODE attribute is set
    to VI_ASRL_WIRE_232_DCE, or VI_ASRL_WIRE_232_AUTO with the
    hardware currently in the DCE state.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_RI_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_RTS_STATE(EnumAttribute):
    """VI_ATTR_ASRL_RTS_STATE is used to manually assert or unassert the
    Request To Send (RTS) output signal.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_RTS_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_STOP_BITS(EnumAttribute):
    """VI_ATTR_ASRL_STOP_BITS is the number of stop bits used to indicate the
    end of a frame. The value VI_ASRL_STOP_ONE5 indicates one-and-one-
    half (1.5) stop bits.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'stop_bits'

    visa_name = 'VI_ATTR_ASRL_STOP_BITS'

    visa_type = 'ViUInt16'

    default = constants.StopBits.one

    read, write, local = True, True, False

    enum_type = constants.StopBits


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_WIRE_MODE(RangeAttribute):
    """

    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_ASRL_WIRE_MODE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_XOFF_CHAR(RangeAttribute):
    """VI_ATTR_ASRL_XOFF_CHAR specifies the value of the XOFF character used
    for XON/XOFF flow control (both directions). If XON/XOFF flow
    control (software handshaking) is not being used, the value of
    this attribute is ignored.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'xoff_char'

    visa_name = 'VI_ATTR_ASRL_XOFF_CHAR'

    visa_type = 'ViUInt8'

    default = 0x13

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_ASRL_XON_CHAR(RangeAttribute):
    """VI_ATTR_ASRL_XON_CHAR specifies the value of the XON character used
    for XON/XOFF flow control (both directions). If XON/XOFF flow
    control (software handshaking) is not being used, the value of
    this attribute is ignored.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR')]

    py_name = 'xon_char'

    visa_name = 'VI_ATTR_ASRL_XON_CHAR'

    visa_type = 'ViUInt8'

    default = 0x11

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFF, []


# Could not generate class for VI_ATTR_BUFFER.html
# Exception:
"""
'list' object has no attribute 'startswith'
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_CMDR_LA(RangeAttribute):
    """VI_ATTR_CMDR_LA is the unique logical address of the commander of the
    VXI device used by the given session.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_CMDR_LA'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 255, [constants.VI_UNKNOWN_LA]


# noinspection PyPep8Naming
class AttrVI_ATTR_DEST_ACCESS_PRIV(RangeAttribute):
    """VI_ATTR_DEST_ACCESS_PRIV specifies the address modifier to be used in
    high-level access operations, such as viOutXX() and viMoveOutXX(),
    when writing to the destination.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_DEST_ACCESS_PRIV'

    visa_type = 'ViUInt16'

    default = constants.VI_DATA_PRIV

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_DEST_BYTE_ORDER(RangeAttribute):
    """VI_ATTR_DEST_BYTE_ORDER specifies the byte order to be used in high-
    level access operations, such as viOutXX() and viMoveOutXX(), when
    writing to the destination.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_DEST_BYTE_ORDER'

    visa_type = 'ViUInt16'

    default = constants.VI_BIG_ENDIAN

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_DEST_INCREMENT(RangeAttribute):
    """VI_ATTR_DEST_INCREMENT is used in the viMoveOutXX() operations to
    specify by how many elements the destination offset is to be
    incremented after every transfer. The default value of this
    attribute is 1 (that is, the destination address will be
    incremented by 1 after each transfer), and the viMoveOutXX()
    operations move into consecutive elements. If this attribute is
    set to 0, the viMoveOutXX() operations will always write to the
    same element, essentially treating the destination as a FIFO
    register.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'MEMACC'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = 'destination_increment'

    visa_name = 'VI_ATTR_DEST_INCREMENT'

    visa_type = 'ViInt32'

    default = 1

    read, write, local = True, True, True

    min_value, max_value, values = 0, 1, []


# noinspection PyPep8Naming
class AttrVI_ATTR_DEV_STATUS_BYTE(RangeAttribute):
    """This attribute specifies the 488-style status byte of the local
    controller or device associated with this session.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_DEV_STATUS_BYTE'

    visa_type = 'ViUInt8'

    default = NotAvailable

    read, write, local = True, True, False

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_DMA_ALLOW_EN(BooleanAttribute):
    """This attribute specifies whether I/O accesses should use DMA (VI_TRUE)
    or Programmed I/O (VI_FALSE). In some implementations, this
    attribute may have global effects even though it is documented to
    be a local attribute. Since this affects performance and not
    functionality, that behavior is acceptable.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = 'allow_dma'

    visa_name = 'VI_ATTR_DMA_ALLOW_EN'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, True, True


# Could not generate class for VI_ATTR_EVENT_TYPE.html
# Exception:
"""
Unknown type: ViEventType. Range: [u'0h to FFFFFFFFh']
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_FDC_CHNL(RangeAttribute):
    """VI_ATTR_FDC_CHNL determines which Fast Data Channel (FDC) will be used
    to transfer the buffer.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_FDC_CHNL'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = 0, 7, []


# noinspection PyPep8Naming
class AttrVI_ATTR_FDC_MODE(RangeAttribute):
    """VI_ATTR_FDC_MODE specifies which Fast Data Channel (FDC) mode to use
    (either normal or stream mode).
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_FDC_MODE'

    visa_type = 'ViUInt16'

    default = constants.VI_FDC_NORMAL

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_FDC_USE_PAIR(BooleanAttribute):
    """Setting VI_ATTR_FDC_USE_PAIR to VI_TRUE specifies to use a channel
    pair for transferring data. Otherwise, only one channel will be
    used.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_FDC_USE_PAIR'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_FILE_APPEND_EN(BooleanAttribute):
    """This attribute specifies whether viReadToFile() will overwrite
    (truncate) or append when opening a file.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_FILE_APPEND_EN'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_ADDR_STATE(EnumAttribute):
    """This attribute shows whether the specified GPIB interface is currently
    addressed to talk or listen, or is not addressed.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'address_state'

    visa_name = 'VI_ATTR_GPIB_ADDR_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.AddressState


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_ATN_STATE(EnumAttribute):
    """This attribute shows the current state of the GPIB ATN (ATtentioN)
    interface line.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'atn_state'

    visa_name = 'VI_ATTR_GPIB_ATN_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_CIC_STATE(BooleanAttribute):
    """This attribute shows whether the specified GPIB interface is currently
    CIC (Controller In Charge).
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'is_controller_in_charge'

    visa_name = 'VI_ATTR_GPIB_CIC_STATE'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_HS488_CBL_LEN(RangeAttribute):
    """This attribute specifies the total number of meters of GPIB cable used
    in the specified GPIB interface.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = ''

    visa_name = 'VI_ATTR_GPIB_HS488_CBL_LEN'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, False

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_NDAC_STATE(EnumAttribute):
    """This attribute shows the current state of the GPIB NDAC (Not Data
    ACcepted) interface line.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'ndac_state'

    visa_name = 'VI_ATTR_GPIB_NDAC_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_PRIMARY_ADDR(RangeAttribute):
    """VI_ATTR_GPIB_PRIMARY_ADDR specifies the primary address of the GPIB
    device used by the given session. For the GPIB INTFC Resource,
    this attribute is Read-Write.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'primary_address'

    visa_name = 'VI_ATTR_GPIB_PRIMARY_ADDR'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, True, False

    min_value, max_value, values = 0, 30, []


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_READDR_EN(BooleanAttribute):
    """VI_ATTR_GPIB_READDR_EN specifies whether to use repeat addressing
    before each read or write operation.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR')]

    py_name = 'enable_repeat_addressing'

    visa_name = 'VI_ATTR_GPIB_READDR_EN'

    visa_type = 'ViBoolean'

    default = True

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_REN_STATE(EnumAttribute):
    """VI_ATTR_GPIB_REN_STATE returns the current state of the GPIB REN
    (Remote ENable) interface line.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'remote_enabled'

    visa_name = 'VI_ATTR_GPIB_REN_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_SECONDARY_ADDR(RangeAttribute):
    """VI_ATTR_GPIB_SECONDARY_ADDR specifies the secondary address of the
    GPIB device used by the given session. For the GPIB INTFC
    Resource, this attribute is Read-Write.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'secondary_address'

    visa_name = 'VI_ATTR_GPIB_SECONDARY_ADDR'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, True, False

    min_value, max_value, values = 0, 30, [constants.VI_NO_SEC_ADDR]


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_SRQ_STATE(EnumAttribute):
    """This attribute shows the current state of the GPIB SRQ (Service
    ReQuest) interface line.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = ''

    visa_name = 'VI_ATTR_GPIB_SRQ_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_SYS_CNTRL_STATE(BooleanAttribute):
    """This attribute shows whether the specified GPIB interface is currently
    the system controller. In some implementations, this attribute may
    be modified only through a configuration utility. On these systems
    this attribute is read-only (RO).
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC')]

    py_name = 'is_system_controller'

    visa_name = 'VI_ATTR_GPIB_SYS_CNTRL_STATE'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, True, False


# noinspection PyPep8Naming
class AttrVI_ATTR_GPIB_UNADDR_EN(BooleanAttribute):
    """VI_ATTR_GPIB_UNADDR_EN specifies whether to unaddress the device (UNT
    and UNL) after each read or write operation.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR')]

    py_name = 'enable_unaddressing'

    visa_name = 'VI_ATTR_GPIB_UNADDR_EN'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_IMMEDIATE_SERV(BooleanAttribute):
    """VI_ATTR_IMMEDIATE_SERV specifies whether the device associated with
    this session is an immediate servant of the controller running
    VISA.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_IMMEDIATE_SERV'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_INTF_INST_NAME(Attribute):
    """VI_ATTR_INTF_INST_NAME specifies human-readable text that describes
    the given interface.
    """
    resources = AllSessionTypes

    py_name = ''

    visa_name = 'VI_ATTR_INTF_INST_NAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_INTF_NUM(RangeAttribute):
    """VI_ATTR_INTF_NUM specifies the board number for the given interface.
    """
    resources = AllSessionTypes

    py_name = 'interface_number'

    visa_name = 'VI_ATTR_INTF_NUM'

    visa_type = 'ViUInt16'

    default = 0

    read, write, local = True, False, False

    min_value, max_value, values = 0x0, 0xFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_INTF_TYPE(RangeAttribute):
    """VI_ATTR_INTF_TYPE specifies the interface type of the given session.
    """
    resources = AllSessionTypes

    py_name = ''

    visa_name = 'VI_ATTR_INTF_TYPE'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_IO_PROT(RangeAttribute):
    """VI_ATTR_IO_PROT specifies which protocol to use. In VXI, you can
    choose normal word serial or fast data channel (FDC). In GPIB, you
    can choose normal or high-speed (HS-488) transfers. In serial,
    TCPIP, or USB RAW, you can choose normal transfers or
    488.2-defined strings. In USB INSTR, you can choose normal or
    vendor-specific transfers.
    """
    resources = [(constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = 'io_protocol'

    visa_name = 'VI_ATTR_IO_PROT'

    visa_type = 'ViUInt16'

    default = constants.VI_PROT_NORMAL

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_MAINFRAME_LA(RangeAttribute):
    """VI_ATTR_MA.infRAME_LA specifies the lowest logical address in the
    mainframe. If the logical address is not known, VI_UNKNOWN_LA is
    returned.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_MAINFRAME_LA'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 255, [constants.VI_UNKNOWN_LA]


# noinspection PyPep8Naming
class AttrVI_ATTR_MANF_ID(RangeAttribute):
    """VI_ATTR_MANF_ID is the manufacturer identification number of the
    device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = 'manufacturer_id'

    visa_name = 'VI_ATTR_MANF_ID'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0x0, 0xFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_MANF_NAME(Attribute):
    """This string attribute is the manufacturer name.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'BACKPLANE'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = 'manufacturer_name'

    visa_name = 'VI_ATTR_MANF_NAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_MAX_QUEUE_LENGTH(RangeAttribute):
    """VI_ATTR_MAX_QUEUE_LENGTH specifies the maximum number of events that
    can be queued at any time on the given session. Events that occur
    after the queue has become full will be discarded.
    """
    resources = AllSessionTypes

    py_name = ''

    visa_name = 'VI_ATTR_MAX_QUEUE_LENGTH'

    visa_type = 'ViUInt32'

    default = 50

    read, write, local = True, True, True

    min_value, max_value, values = 0x1, 0xFFFFFFFF, []


# Could not generate class for VI_ATTR_MEM_BASE.html
# Exception:
"""
Unknown type: VI_ATTR_MEM_BASE:
ViBusAddress
VI_ATTR_MEM_BASE_32:
ViUInt32
VI_ATTR_MEM_BASE_64:
ViUInt64. Range: [u'VI_ATTR_MEM_BASE:', u'0h to FFFFFFFFh for 32\u2011bit applications', u'0h to FFFFFFFFFFFFFFFFh for 64\u2011bit applications', u'VI_ATTR_MEM_BASE_32:', u'0h to FFFFFFFFh', u'VI_ATTR_MEM_BASE_64:', u'0h to FFFFFFFFFFFFFFFFh']
"""


# Could not generate class for VI_ATTR_MEM_SIZE.html
# Exception:
"""
Unknown type: VI_ATTR_MEM_SIZE:
ViBusSize
VI_ATTR_MEM_SIZE_32:
ViUInt32
VI_ATTR_MEM_SIZE_64:
ViUInt64. Range: [u'VI_ATTR_MEM_SIZE:', u'0h to FFFFFFFFh for 32\u2011bit applications', u'0h to FFFFFFFFFFFFFFFFh for 64\u2011bit applications', u'VI_ATTR_MEM_SIZE_32:', u'0h to FFFFFFFFh', u'VI_ATTR_MEM_SIZE_64:', u'0h to FFFFFFFFFFFFFFFFh']
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_MEM_SPACE(RangeAttribute):
    """VI_ATTR_MEM_SPACE specifies the VXIbus address space used by the
    device. The three types are A16, A24, or A32 memory address space.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_MEM_SPACE'

    visa_type = 'ViUInt16'

    default = constants.VI_A16_SPACE

    read, write, local = True, False, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_MODEL_CODE(RangeAttribute):
    """VI_ATTR_MODEL_CODE specifies the model code for the device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = 'model_code'

    visa_name = 'VI_ATTR_MODEL_CODE'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0x0, 0xFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_MODEL_NAME(Attribute):
    """This string attribute is the model name of the device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'BACKPLANE'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = 'model_name'

    visa_name = 'VI_ATTR_MODEL_NAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_ACTUAL_LWIDTH(ValuesAttribute):
    """VI_ATTR_PXI_ACTUAL_LWIDTH specifies the PCI Express link width
    negotiated between the PCI Express host controller and the device.
    A value of –1 indicates that the device is not a PXI/PCI Express
    device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_ACTUAL_LWIDTH'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    values = [-1, 1, 2, 4, 8, 16]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_BUS_NUM(RangeAttribute):
    """VI_ATTR_PXI_BUS_NUM specifies the PCI bus number of this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_BUS_NUM'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 255, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_CHASSIS(RangeAttribute):
    """VI_ATTR_PXI_CHASSIS specifies the PXI chassis number of this device. A
    value of –1 means the chassis number is unknown.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_CHASSIS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 255, [-1]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_DEST_TRIG_BUS(RangeAttribute):
    """VI_ATTR_PXI_DEST_TRIG_BUS specifies the segment to use to qualify
    trigDest in viMapTrigger.
    """
    resources = [(constants.InterfaceType.pxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_DEST_TRIG_BUS'

    visa_type = 'ViInt16'

    default = -1

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_DEV_NUM(RangeAttribute):
    """This is the PXI device number.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_DEV_NUM'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 31, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_DSTAR_BUS(RangeAttribute):
    """VI_ATTR_PXI_DSTAR_BUS specifies the differential star bus number of
    this device. A value of –1 means the chassis is unidentified or
    does not have a timing slot.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_DSTAR_BUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_DSTAR_SET(RangeAttribute):
    """

    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_DSTAR_SET'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 16, [-1]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_FUNC_NUM(RangeAttribute):
    """This is the PCI function number of the PXI/PCI resource. For most
    devices, the function number is 0, but a multifunction device may
    have a function number up to 7. The meaning of a function number
    other than 0 is device specific.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_FUNC_NUM'

    visa_type = 'ViUInt16'

    default = 0

    read, write, local = True, False, False

    min_value, max_value, values = 0, 7, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_IS_EXPRESS(BooleanAttribute):
    """VI_ATTR_PXI_IS_EXPRESS specifies whether the device is PXI/PCI or
    PXI/PCI Express.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_IS_EXPRESS'

    visa_type = 'ViBoolean'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_MAX_LWIDTH(ValuesAttribute):
    """VI_ATTR_PXI_MAX_LWIDTH specifies the maximum PCI Express link width of
    the device. A value of –1 indicates that the device is not a
    PXI/PCI Express device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_MAX_LWIDTH'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    values = [-1, 1, 2, 4, 8, 16]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_MEM_BASE_BARX(RangeAttribute):
    """PXI memory base address assigned to the specified BAR. If the value of
    the corresponding VI_ATTR_PXI_MEM_TYPE_BARx is VI_PXI_ADDR_NONE,
    the value of this attribute is meaningless for the given PXI
    device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_MEM_BASE_BARX'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFFFFFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_MEM_SIZE_BARX(RangeAttribute):
    """Memory size used by the device in the specified BAR. If the value of
    the corresponding VI_ATTR_PXI_MEM_TYPE_BARx is VI_PXI_ADDR_NONE,
    the value of this attribute is meaningless for the given PXI
    device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_MEM_SIZE_BARX'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFFFFFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_MEM_TYPE_BARX(RangeAttribute):
    """Memory type used by the device in the specified BAR (if applicable).
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_MEM_TYPE_BARX'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_SLOT_LBUS_LEFT(RangeAttribute):
    """VI_ATTR_PXI_SLOT_LBUS_LEFT specifies the slot number or special
    feature connected to the local bus left lines of this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_SLOT_LBUS_LEFT'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 1, 18, [constants.VI_PXI_LBUS_UNKNOWN,
                                           constants.VI_PXI_LBUS_NONE,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_0,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_1,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_2,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_3,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_4,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_5,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_6,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_7,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_8,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_9,
                                           constants.VI_PXI_STAR_TRIG_CONTROLLER,
                                           constants.VI_PXI_LBUS_SCXI]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_SLOT_LBUS_RIGHT(RangeAttribute):
    """VI_ATTR_PXI_SLOT_LBUS_RIGHT specifies the slot number or special
    feature connected to the local bus right lines of this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_SLOT_LBUS_RIGHT'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 1, 18, [constants.VI_PXI_LBUS_UNKNOWN,
                                           constants.VI_PXI_LBUS_NONE,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_0,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_1,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_2,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_3,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_4,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_5,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_6,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_7,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_8,
                                           constants.VI_PXI_LBUS_STAR_TRIG_BUS_9,
                                           constants.VI_PXI_STAR_TRIG_CONTROLLER,
                                           constants.VI_PXI_LBUS_SCXI]

# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_SLOT_LWIDTH(ValuesAttribute):
    """VI_ATTR_PXI_SLOT_LWIDTH specifies the PCI Express link width of the
    PXI Express peripheral slot in which the device resides. A value
    of –1 indicates that the device is not a PXI Express device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_SLOT_LWIDTH'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    values = [-1, 1, 4, 8]


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_SLOTPATH(Attribute):
    """VI_ATTR_PXI_SLOTPATH specifies the slot path of this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_SLOTPATH'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_SRC_TRIG_BUS(RangeAttribute):
    """VI_ATTR_PXI_SRC_TRIG_BUS specifies the segment to use to qualify
    trigSrc in viMapTrigger.
    """
    resources = [(constants.InterfaceType.pxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_SRC_TRIG_BUS'

    visa_type = 'ViInt16'

    default = -1

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_STAR_TRIG_BUS(RangeAttribute):
    """VI_ATTR_PXI_STAR_TRIG_BUS specifies the star trigger bus number of
    this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_STAR_TRIG_BUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_STAR_TRIG_LINE(RangeAttribute):
    """VI_ATTR_PXI_STAR_TRIG_LINE specifies the PXI_STAR line connected to
    this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_STAR_TRIG_LINE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_PXI_TRIG_BUS(RangeAttribute):
    """VI_ATTR_PXI_TRIG_BUS specifies the trigger bus number of this device.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_PXI_TRIG_BUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RD_BUF_OPER_MODE(RangeAttribute):
    """VI_ATTR_RD_BUF_OPER_MODE specifies the operational mode of the
    formatted I/O read buffer. When the operational mode is set to
    VI_FLUSH_DISABLE (default), the buffer is flushed only on explicit
    calls to viFlush(). If the operational mode is set to
    VI_FLUSH_ON_ACCESS, the read buffer is flushed every time a
    viScanf() (or related) operation completes.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_RD_BUF_OPER_MODE'

    visa_type = 'ViUInt16'

    default = constants.VI_FLUSH_DISABLE

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RD_BUF_SIZE(RangeAttribute):
    """This is the current size of the formatted I/O input buffer for this
    session. The user can modify this value by calling viSetBuf().
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_RD_BUF_SIZE'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, True

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RM_SESSION(RangeAttribute):
    """This is the current size of the formatted I/O input buffer for this
    session. The user can modify this value by calling viSetBuf().

    Not implemented as resource property, use .resource_manager.session
    """
    resources = AllSessionTypes

    # See docstring
    py_name = ''

    visa_name = 'VI_ATTR_RM_SESSION'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, True

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_CLASS(Attribute):
    """VI_ATTR_RSRC_CLASS specifies the resource class (for example, "INSTR")
    as defined by the canonical resource name.
    """
    resources = AllSessionTypes

    py_name = 'resource_class'

    visa_name = 'VI_ATTR_RSRC_CLASS'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_IMPL_VERSION(RangeAttribute):
    """VI_ATTR_RSRC_IMPL_VERSION is the resource version that uniquely identifies
    each of the different revisions or implementations of a resource. This
    attribute value is defined by the individual manufacturer and increments
    with each new revision. The format of the value has the upper 12 bits as
    the major number of the version, the next lower 12 bits as the minor number
    of the version, and the lowest 8 bits as the sub-minor number of the version.
    """
    resources = AllSessionTypes

    py_name = 'implementation_version'

    visa_name = 'VI_ATTR_RSRC_IMPL_VERSION'

    visa_type = 'ViVersion'

    default = NotAvailable

    read, write, local = True, False, True

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_LOCK_STATE(EnumAttribute):
    """VI_ATTR_RSRC_LOCK_STATE indicates the current locking state of the
    resource. The resource can be unlocked, locked with an exclusive
    lock, or locked with a shared lock.
    """
    resources = AllSessionTypes

    py_name = 'lock_state'

    visa_name = 'VI_ATTR_RSRC_LOCK_STATE'

    visa_type = 'ViAccessMode'

    default = constants.VI_NO_LOCK

    read, write, local = True, False, False

    enum_type = constants.AccessModes


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_MANF_ID(RangeAttribute):
    """VI_ATTR_RSRC_MANF_ID is a value that corresponds to the VXI manufacturer
    ID of the vendor that implemented the VISA library. This attribute is not
    related to the device manufacturer attributes.
    """
    resources = AllSessionTypes

    py_name = ''

    visa_name = 'VI_ATTR_RSRC_MANF_ID'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0x3FFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_MANF_NAME(Attribute):
    """VI_ATTR_RSRC_MANF_NAME is a string that corresponds to the manufacturer
    name of the vendor that implemented the VISA library. This attribute is not
    related to the device manufacturer attributes.

    Note  The value of this attribute is for display purposes only and not for
    programmatic decisions, as the value can differ between VISA implementations
    and/or revisions.
    """
    resources = AllSessionTypes

    py_name = 'resource_manufacturer_name'

    visa_name = 'VI_ATTR_RSRC_MANF_NAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_NAME(Attribute):
    """VI_ATTR_RSRC_MANF_NAME is a string that corresponds to the manufacturer
    name of the vendor that implemented the VISA library. This attribute is not
    related to the device manufacturer attributes.

    Note  The value of this attribute is for display purposes only and not for
    programmatic decisions, as the value can differ between VISA implementations
    and/or revisions.
    """
    resources = AllSessionTypes

    py_name = 'resource_name'

    visa_name = 'VI_ATTR_RSRC_NAME'

    visa_type = 'ViRsrc'

    default = NotAvailable

    read, write, local = True, False, False


# noinspection PyPep8Naming
class AttrVI_ATTR_RSRC_SPEC_VERSION(RangeAttribute):
    """VI_ATTR_RSRC_SPEC_VERSION is the resource version that uniquely identifies
    the version of the VISA specification to which the implementation is compliant.
    The format of the value has the upper 12 bits as the major number of the version,
    the next lower 12 bits as the minor number of the version, and the lowest 8 bits
    as the sub-minor number of the version. The current VISA specification defines
    the value to be 00300000h.
    """
    resources = AllSessionTypes

    py_name = 'spec_version'

    visa_name = 'VI_ATTR_RSRC_SPEC_VERSION'

    visa_type = 'ViVersion'

    default = 0x00300000

    read, write, local = True, False, True

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_SEND_END_EN(BooleanAttribute):
    """VI_ATTR_SEND_END_EN specifies whether to assert END during the
    transfer of the last byte of the buffer.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = 'send_end'

    visa_name = 'VI_ATTR_SEND_END_EN'

    visa_type = 'ViBoolean'

    default = True

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_SLOT(RangeAttribute):
    """VI_ATTR_SLOT specifies the physical slot location of the device. If
    the slot number is not known, VI_UNKNOWN_SLOT is returned.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_SLOT'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'VXI', u'0 to 12', u'VI_UNKNOWN_SLOT (\u20131)', u'PXI', u'1 to 18', u'VI_UNKNOWN_SLOT (\u20131)'], ValueError('too many values to unpack',)


# noinspection PyPep8Naming
class AttrVI_ATTR_SRC_ACCESS_PRIV(RangeAttribute):
    """VI_ATTR_SRC_ACCESS_PRIV specifies the address modifier to be used in
    high-level access operations, such as viInXX() and viMoveInXX(),
    when reading from the source.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_SRC_ACCESS_PRIV'

    visa_type = 'ViUInt16'

    default = constants.VI_DATA_PRIV

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_SRC_BYTE_ORDER(RangeAttribute):
    """VI_ATTR_SRC_BYTE_ORDER specifies the byte order to be used in high-
    level access operations, such as viInXX() and viMoveInXX(), when
    reading from the source.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_SRC_BYTE_ORDER'

    visa_type = 'ViUInt16'

    default = constants.VI_BIG_ENDIAN

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_SRC_INCREMENT(RangeAttribute):
    """VI_ATTR_SRC_INCREMENT is used in the viMoveInXX() operations to
    specify by how many elements the source offset is to be
    incremented after every transfer. The default value of this
    attribute is 1 (that is, the source address will be incremented by
    1 after each transfer), and the viMoveInXX() operations move from
    consecutive elements. If this attribute is set to 0, the
    viMoveInXX() operations will always read from the same element,
    essentially treating the source as a FIFO register.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'MEMACC'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = 'source_increment'

    visa_name = 'VI_ATTR_SRC_INCREMENT'

    visa_type = 'ViInt32'

    default = 1

    read, write, local = True, True, True

    min_value, max_value, values = 0, 1, []


# noinspection PyPep8Naming
class AttrVI_ATTR_SUPPRESS_END_EN(BooleanAttribute):
    """VI_ATTR_SUPPRESS_END_EN is relevant only in viRead and related
    operations.
    """
    resources = [(constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_SUPPRESS_END_EN'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_ADDR(Attribute):
    """This is the TCPIP address of the device to which the session is
    connected. This string is formatted in dot notation.
    """
    resources = [(constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_ADDR'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_DEVICE_NAME(Attribute):
    """This specifies the LAN device name used by the VXI-11 or LXI protocol
    during connection.
    """
    resources = [(constants.InterfaceType.tcpip, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_DEVICE_NAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_HOSTNAME(Attribute):
    """This specifies the host name of the device. If no host name is
    available, this attribute returns an empty string.
    """
    resources = [(constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_HOSTNAME'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_KEEPALIVE(BooleanAttribute):
    """Setting this attribute to TRUE requests that a TCP/IP provider enable
    the use of keep-alive packets on TCP connections. After the system
    detects that a connection was dropped, VISA returns a lost
    connection error code on subsequent I/O calls on the session. The
    time required for the system to detect that the connection was
    dropped is dependent on the system and is not settable.
    """
    resources = [(constants.InterfaceType.tcpip, 'SOCKET')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_KEEPALIVE'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_NODELAY(BooleanAttribute):
    """The Nagle algorithm is disabled when this attribute is enabled (and
    vice versa). The Nagle algorithm improves network performance by
    buffering "send" data until a full-size packet can be sent. This
    attribute is enabled by default in VISA to verify that synchronous
    writes get flushed immediately.
    """
    resources = [(constants.InterfaceType.tcpip, 'SOCKET')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_NODELAY'

    visa_type = 'ViBoolean'

    default = True

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_TCPIP_PORT(RangeAttribute):
    """This specifies the port number for a given TCPIP address. For a TCPIP
    SOCKET Resource, this is a required part of the address string.
    """
    resources = [(constants.InterfaceType.tcpip, 'SOCKET')]

    py_name = ''

    visa_name = 'VI_ATTR_TCPIP_PORT'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_TERMCHAR(RangeAttribute):
    """VI_ATTR_TERMCHAR is the termination character. When the termination
    character is read and VI_ATTR_TERMCHAR_EN is enabled during a read
    operation, the read operation terminates.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_TERMCHAR'

    visa_type = 'ViUInt8'

    default = 0x0A # (linefeed)

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_TERMCHAR_EN(BooleanAttribute):
    """VI_ATTR_TERMCHAR_EN is a flag that determines whether the read
    operation should terminate when a termination character is
    received. This attribute is ignored if VI_ATTR_ASRL_END_IN is set
    to VI_ASRL_END_TERMCHAR. This attribute is valid for both raw I/O
    (viRead) and formatted I/O (viScanf).
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_TERMCHAR_EN'

    visa_type = 'ViBoolean'

    default = False

    read, write, local = True, True, True


# noinspection PyPep8Naming
class AttrVI_ATTR_TMO_VALUE(RangeAttribute):
    """VI_ATTR_TMO_VALUE specifies the minimum timeout value to use (in
    milliseconds) when accessing the device associated with the given
    session. A timeout value of VI_TMO_IMMEDIATE means that operations
    should never wait for the device to respond. A timeout value of
    VI_TMO_INFINITE disables the timeout mechanism.
    """
    resources = AllSessionTypes

    py_name = ''

    visa_name = 'VI_ATTR_TMO_VALUE'

    visa_type = 'ViUInt32'

    default = 2000

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFFFFFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_TRIG_ID(ValuesAttribute):
    """VI_ATTR_TRIG_ID is the identifier for the current triggering
    mechanism.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'BACKPLANE'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.vxi, 'BACKPLANE'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_TRIG_ID'

    visa_type = 'ViInt16'

    default = constants.VI_TRIG_SW

    read, write, local = True, True, True

    values = [] #TODO


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_ALT_SETTING(RangeAttribute):
    """VI_ATTR_USB_ALT_SETTING specifies the USB alternate setting used by
    this USB interface.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_ALT_SETTING'

    visa_type = 'ViInt16'

    default = 0

    read, write, local = True, True, False

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_BULK_IN_PIPE(RangeAttribute):
    """VI_ATTR_USB_BULK_IN_PIPE specifies the endpoint address of the USB
    bulk-in pipe used by the given session. An initial value of -1
    signifies that this resource does not have any bulk-in pipes. This
    endpoint is used in viRead and related operations.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_BULK_IN_PIPE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = 0x81, 0x8F, [-1]


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_BULK_IN_STATUS(RangeAttribute):
    """VI_ATTR_USB_BULK_IN_STATUS specifies whether the USB bulk-in pipe used
    by the given session is stalled or ready. This attribute can be
    set to only VI_USB_PIPE_READY.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_BULK_IN_STATUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_BULK_OUT_PIPE(RangeAttribute):
    """VI_ATTR_USB_BULK_OUT_PIPE specifies the endpoint address of the USB
    bulk-out or interrupt-out pipe used by the given session. An
    initial value of –1 signifies that this resource does not have any
    bulk-out or interrupt-out pipes. This endpoint is used in viWrite
    and related operations.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_BULK_OUT_PIPE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = 0x01, 0x0F, [-1]


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_BULK_OUT_STATUS(RangeAttribute):
    """VI_ATTR_USB_BULK_OUT_STATUS specifies whether the USB bulk-out or
    interrupt-out pipe used by the given session is stalled or ready.
    This attribute can be set to only VI_USB_PIPE_READY.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_BULK_OUT_STATUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_CLASS(RangeAttribute):
    """VI_ATTR_USB_CLASS specifies the USB class used by this USB interface.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_CLASS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_CTRL_PIPE(RangeAttribute):
    """VI_ATTR_USB_CTRL_PIPE specifies the endpoint address of the USB
    control pipe used by the given session. A value of 0 signifies
    that the default control pipe will be used. This endpoint is used
    in viUsbControlIn and viUsbControlOut operations. Nonzero values
    may not be supported on all platforms.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_CTRL_PIPE'

    visa_type = 'ViInt16'

    default = 0x00

    read, write, local = True, True, True

    min_value, max_value, values = 0x00, 0x0F, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_END_IN(ValuesAttribute):
    """VI_ATTR_USB_END_IN indicates the method used to terminate read
    operations.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_END_IN'

    visa_type = 'ViUInt16'

    default = constants.VI_USB_END_SHORT_OR_COUNT

    read, write, local = True, True, True

    values = [constants.VI_USB_END_NONE,
              constants.VI_USB_END_SHORT,
              constants.VI_USB_END_SHORT_OR_COUNT]


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_INTFC_NUM(RangeAttribute):
    """VI_ATTR_USB_INTFC_NUM specifies the USB interface number used by the
    given session.
    """
    resources = [(constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW')]

    py_name = 'interface_number'

    visa_name = 'VI_ATTR_USB_INTFC_NUM'

    visa_type = 'ViInt16'

    default = 0

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFE, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_INTR_IN_PIPE(RangeAttribute):
    """VI_ATTR_USB_INTR_IN_PIPE specifies the endpoint address of the USB
    interrupt-in pipe used by the given session. An initial value of
    -1 signifies that this resource does not have any interrupt-in
    pipes. This endpoint is used in viEnableEvent for
    VI_EVENT_USB_INTR.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_INTR_IN_PIPE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = 0x81, 0x8F, [-1]


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_INTR_IN_STATUS(RangeAttribute):
    """VI_ATTR_USB_INTR_IN_STATUS specifies whether the USB interrupt-in pipe
    used by the given session is stalled or ready. This attribute can
    be set to only VI_USB_PIPE_READY.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_INTR_IN_STATUS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = -32768, 32767, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_MAX_INTR_SIZE(RangeAttribute):
    """VI_ATTR_USB_MAX_INTR_SIZE specifies the maximum size of data that will
    be stored by any given USB interrupt. If a USB interrupt contains
    more data than this size, the data in excess of this size will be
    lost.
    """
    resources = [(constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW')]

    py_name = 'maximum_interrupt_size'

    visa_name = 'VI_ATTR_USB_MAX_INTR_SIZE'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, True, True

    min_value, max_value, values = 0, 0xFFFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_NUM_INTFCS(RangeAttribute):
    """VI_ATTR_USB_NUM_INTFCS specifies the number of interfaces supported by
    this USB device.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_NUM_INTFCS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 1, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_NUM_PIPES(RangeAttribute):
    """VI_ATTR_USB_NUM_PIPES specifies the number of pipes supported by this
    USB interface. This does not include the default control pipe.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_NUM_PIPES'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 30, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_PROTOCOL(RangeAttribute):
    """VI_ATTR_USB_PROTOCOL specifies the USB protocol used by this USB
    interface.
    """
    resources = [(constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW')]

    py_name = 'usb_protocol'

    visa_name = 'VI_ATTR_USB_PROTOCOL'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFF, []


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_SERIAL_NUM(Attribute):
    """VI_ATTR_USB_SERIAL_NUM specifies the USB serial number of this device.
    """
    resources = [(constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW')]

    py_name = 'serial_number'

    visa_name = 'VI_ATTR_USB_SERIAL_NUM'

    visa_type = 'ViString'

    default = NotAvailable

    read, write, local = True, False, False

    # [u'N/A']


# noinspection PyPep8Naming
class AttrVI_ATTR_USB_SUBCLASS(RangeAttribute):
    """VI_ATTR_USB_SUBCLASS specifies the USB subclass used by this USB
    interface.
    """
    resources = [(constants.InterfaceType.usb, 'RAW')]

    py_name = ''

    visa_name = 'VI_ATTR_USB_SUBCLASS'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 0xFF, []


# Could not generate class for VI_ATTR_USER_DATA.html
# Exception:
"""
Unknown type: VI_ATTR_USER_DATA:
ViAddr
VI_ATTR_USER_DATA_32:
ViUInt32
VI_ATTR_USER_DATA_64:
ViUInt64. Range: [u'VI_ATTR_USER_DATA:', u'Not specified', u'VI_ATTR_USER_DATA_32:', u'0h to FFFFFFFFh', u'VI_ATTR_USER_DATA_64:', u'0h to FFFFFFFFFFFFFFFFh']
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_DEV_CLASS(RangeAttribute):
    """This attribute represents the VXI-defined device class to which the
    resource belongs, either message based (VI_VXI_CLASS_MESSAGE),
    register based (VI_VXI_CLASS_REGISTER), extended
    (VI_VXI_CLASS_EXTENDED), or memory (VI_VXI_CLASS_MEMORY). VME
    devices are usually either register based or belong to a
    miscellaneous class (VI_VXI_CLASS_OTHER).
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_DEV_CLASS'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_LA(RangeAttribute):
    """For an INSTR session, VI_ATTR_VXI_LA specifies the logical address of
    the VXI or VME device used by the given session. For a MEMACC or
    SERVANT session, this attribute specifies the logical address of
    the local controller.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_LA'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 511, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_TRIG_DIR(RangeAttribute):
    """VI_ATTR_TRIG_DIR is a bit map of the directions of the mapped TTL
    trigger lines. Bits 0-7 represent TTL triggers 0-7 respectively. A
    bit's value of 0 means the line is routed out of the frame, and a
    value of 1 means into the frame. In order for a direction to be
    set, the line must also be enabled using
    VI_ATTR_VXI_TRIG_LINES_EN.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_TRIG_DIR'

    visa_type = 'ViUInt16'

    default = 0

    read, write, local = True, True, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_TRIG_LINES_EN(RangeAttribute):
    """VI_ATTR_VXI_TRIG_LINES_EN is a bit map of what VXI TLL triggers have
    mappings. Bits 0-7 represent TTL triggers 0-7 respectively. A
    bit's value of 0 means the trigger line is unmapped, and 1 means a
    mapping exists. Use VI_ATTR_VXI_TRIG_DIR to set an enabled line's
    direction.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_TRIG_LINES_EN'

    visa_type = 'ViUInt16'

    default = 0

    read, write, local = True, True, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_TRIG_STATUS(RangeAttribute):
    """This attribute shows the current state of the VXI trigger lines. This
    is a bit vector with bits 0-9 corresponding to VI_TRIG_TTL0
    through VI_TRIG_ECL1.
    """
    resources = [(constants.InterfaceType.vxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_TRIG_STATUS'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_TRIG_SUPPORT(RangeAttribute):
    """This attribute shows which VXI trigger lines this implementation
    supports. This is a bit vector with bits 0-9 corresponding to
    VI_TRIG_TTL0 through VI_TRIG_ECL1.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_TRIG_SUPPORT'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 4294967295, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_VME_INTR_STATUS(RangeAttribute):
    """This attribute shows the current state of the VXI/VME interrupt lines.
    This is a bit vector with bits 0-6 corresponding to interrupt
    lines 1-7.
    """
    resources = [(constants.InterfaceType.vxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_VME_INTR_STATUS'

    visa_type = 'ViUInt16'

    default = NotAvailable

    read, write, local = True, False, False

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_VXI_VME_SYSFAIL_STATE(EnumAttribute):
    """This attribute shows the current state of the VXI/VME SYSFAIL (SYStem
    FAILure) backplane line.
    """
    resources = [(constants.InterfaceType.vxi, 'BACKPLANE')]

    py_name = ''

    visa_name = 'VI_ATTR_VXI_VME_SYSFAIL_STATE'

    visa_type = 'ViInt16'

    default = NotAvailable

    read, write, local = True, False, False

    enum_type = constants.LineState


# noinspection PyPep8Naming
class AttrVI_ATTR_WIN_ACCESS(RangeAttribute):
    """VI_ATTR_WIN_ACCESS specifies the modes in which the current window may
    be accessed.
    """
    resources = [(constants.InterfaceType.pxi, 'INSTR'),
                 (constants.InterfaceType.pxi, 'MEMACC'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_WIN_ACCESS'

    visa_type = 'ViUInt16'

    default = constants.VI_NMAPPED

    read, write, local = True, False, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_WIN_ACCESS_PRIV(RangeAttribute):
    """VI_ATTR_WIN_ACCESS_PRIV specifies the address modifier to be used in
    low-level access operations, such as viMapAddress(), viPeekXX(),
    and viPokeXX(), when accessing the mapped window.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_WIN_ACCESS_PRIV'

    visa_type = 'ViUInt16'

    default = constants.VI_DATA_PRIV

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# Could not generate class for VI_ATTR_WIN_BASE_ADDR.html
# Exception:
"""
Unknown type: VI_ATTR_WIN_BASE_ADDR:
ViBusAddress
VI_ATTR_WIN_BASE_ADDR_32:
ViUInt32
VI_ATTR_WIN_BASE_ADDR_64:
ViUInt64. Range: [u'VI_ATTR_WIN_BASE_ADDR:', u'0h to FFFFFFFFh for 32\u2011bit applications', u'0h to FFFFFFFFFFFFFFFFh for 64\u2011bit applications', u'VI_ATTR_WIN_BASE_ADDR_32:', u'0h to FFFFFFFFh', u'VI_ATTR_WIN_BASE_ADDR_64:', u'0h to FFFFFFFFFFFFFFFFh']
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_WIN_BYTE_ORDER(RangeAttribute):
    """VI_ATTR_WIN_BYTE_ORDER specifies the byte order to be used in low-
    level access operations, such as viMapAddress(), viPeekXX(), and
    viPokeXX(), when accessing the mapped window.
    """
    resources = [(constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'MEMACC')]

    py_name = ''

    visa_name = 'VI_ATTR_WIN_BYTE_ORDER'

    visa_type = 'ViUInt16'

    default = constants.VI_BIG_ENDIAN

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# Could not generate class for VI_ATTR_WIN_SIZE.html
# Exception:
"""
Unknown type: VI_ATTR_WIN_SIZE:
ViBusSize
VI_ATTR_WIN_SIZE_32:
ViUInt32
VI_ATTR_WIN_SIZE_64:
ViUInt64. Range: [u'VI_ATTR_WIN_SIZE:', u'0h to FFFFFFFFh for 32\u2011bit applications', u'0h to FFFFFFFFFFFFFFFFh for 64\u2011bit applications', u'VI_ATTR_WIN_SIZE_32:', u'0h to FFFFFFFFh', u'VI_ATTR_WIN_SIZE_64:', u'0h to FFFFFFFFFFFFFFFFh']
"""


# noinspection PyPep8Naming
class AttrVI_ATTR_WR_BUF_OPER_MODE(RangeAttribute):
    """VI_ATTR_WR_BUF_OPER_MODE specifies the operational mode of the
    formatted I/O write buffer. When the operational mode is set to
    VI_FLUSH_WHEN_FULL (default), the buffer is flushed when an END
    indicator is written to the buffer, or when the buffer fills up.
    If the operational mode is set to VI_FLUSH_ON_ACCESS, the write
    buffer is flushed under the same conditions, and also every time a
    viPrintf() (or related) operation completes.
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_WR_BUF_OPER_MODE'

    visa_type = 'ViUInt16'

    default = constants.VI_FLUSH_WHEN_FULL

    read, write, local = True, True, True

    min_value, max_value, values = 0, 65535, []


# noinspection PyPep8Naming
class AttrVI_ATTR_WR_BUF_SIZE(RangeAttribute):
    """This is the current size of the formatted I/O output buffer for this
    session. The user can modify this value by calling viSetBuf().
    """
    resources = [(constants.InterfaceType.gpib, 'INSTR'),
                 (constants.InterfaceType.gpib, 'INTFC'),
                 (constants.InterfaceType.asrl, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'INSTR'),
                 (constants.InterfaceType.tcpip, 'SOCKET'),
                 (constants.InterfaceType.usb, 'INSTR'),
                 (constants.InterfaceType.usb, 'RAW'),
                 (constants.InterfaceType.vxi, 'INSTR'),
                 (constants.InterfaceType.vxi, 'SERVANT')]

    py_name = ''

    visa_name = 'VI_ATTR_WR_BUF_SIZE'

    visa_type = 'ViUInt32'

    default = NotAvailable

    read, write, local = True, False, True

    min_value, max_value, values = 0, 4294967295, []

