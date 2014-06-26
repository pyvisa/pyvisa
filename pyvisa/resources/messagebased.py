
import time
import warnings
import contextlib
from enum import IntEnum

from .. import logger
from ..constants import *
from .. import errors
from ..util import (warning_context, split_kwargs, warn_for_invalid_kwargs,
                    parse_ascii, parse_binary)

from .resource import Resource

# The bits in the bitfield mean the following:
#
# bit number   if set / if not set
#     0          binary/ascii
#     1          double/single (IEEE floating point)
#     2          big-endian/little-endian
#
# This leads to the following constants:

ascii      = 0
single     = 1
double     = 3
big_endian = 4

CR = '\r'
LF = '\n'


class MessageBasedInstrument(Resource):
    """Class for all kinds of Instruments.

    It can be instantiated, however, if you want to use special features of a
    certain interface system (GPIB, USB, RS232, etc), you must instantiate one
    of its child classes.

    :param resource_name: the instrument's resource name or an alias,
                          may be taken from the list from
                          `list_resources` method from a ResourceManager.
    :param timeout: the VISA timeout for each low-level operation in
                    milliseconds.
    :param term_chars: the termination characters for this device.
    :param chunk_size: size of data packets in bytes that are read from the
                       device.
    :param lock: whether you want to have exclusive access to the device.
                 Default: VI_NO_LOCK
    :param ask_delay: waiting time in seconds after each write command.
                      Default: 0.0
    :param send_end: whether to assert end line after each write command.
                     Default: True
    :param values_format: floating point data value format. Default: ascii (0)
    """

    #: Termination character sequence (Legacy, to be removed in 1.6).
    __term_chars = None

    DEFAULT_KWARGS = {'read_termination': None,
                      'write_termination': CR + LF,
                      #: How many bytes are read per low-level call.
                      'chunk_size': 20 * 1024,
                      #: Seconds to wait between write and read operations inside ask.
                      'ask_delay': 0.0,
                      'send_end': True,
                      #: floating point data value format
                      'values_format': ascii,
                      #: encoding of the messages
                      'encoding': 'ascii'}

    ALL_KWARGS = dict(DEFAULT_KWARGS, **Resource.DEFAULT_KWARGS)

    def __init__(self, resource_name, resource_manager=None, **kwargs):
        skwargs, pkwargs = split_kwargs(kwargs,
                                        MessageBasedInstrument.DEFAULT_KWARGS.keys(),
                                        Resource.DEFAULT_KWARGS.keys())

        self._read_termination = None
        self._write_termination = None

        if 'term_chars' in kwargs:
            kwargs['read_termination'] = kwargs['term_chars']
            kwargs['write_termination'] = kwargs['term_chars']

        super(MessageBasedInstrument, self).__init__(resource_name, resource_manager, **pkwargs)

        for key, value in MessageBasedInstrument.DEFAULT_KWARGS.items():
            setattr(self, key, skwargs.get(key, value))

        if not self.resource_class:
            warnings.warn("resource class of instrument could not be determined",
                          stacklevel=2)
        elif self.resource_class not in ("INSTR", "RAW", "SOCKET"):
            warnings.warn("given resource was not an INSTR but %s"
                          % self.resource_class, stacklevel=2)

    @property
    def encoding(self):
        """Encoding used for read and write operations.
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        _ = 'test encoding'.encode(encoding).decode(encoding)
        self._encoding = encoding

    @property
    def read_termination(self):
        """Read termination character.
        """
        return self._read_termination

    @read_termination.setter
    def read_termination(self, value):

        if value:
            # termination character, the rest is just used for verification after
            # each read operation.
            last_char = value[-1:]
            # Consequently, it's illogical to have the real termination character
            # twice in the sequence (otherwise reading would stop prematurely).

            if last_char in value[:-1]:
                raise ValueError("ambiguous ending in termination characters")

            self.set_visa_attribute(VI_ATTR_TERMCHAR, ord(last_char))
            self.set_visa_attribute(VI_ATTR_TERMCHAR_EN, VI_TRUE)
        else:
            self.set_visa_attribute(VI_ATTR_TERMCHAR_EN, VI_FALSE)

        self._read_termination = value

    @property
    def write_termination(self):
        """Writer termination character.
        """
        return self._write_termination

    @write_termination.setter
    def write_termination(self, value):
        self._write_termination = value

    def write_raw(self, message):
        """Write a string message to the device.

        The term_chars are appended to it, unless they are already.

        :param message: the message to be sent.
        :type message: bytes
        :return: number of bytes written.
        :rtype: int
        """
        return self.visalib.write(self.session, message)

    def write(self, message, termination=None, encoding=None):
        """Write a string message to the device.

        The term_chars are appended to it, unless they are already.

        :param message: the message to be sent.
        :type message: unicode (Py2) or str (Py3)
        :return: number of bytes written.
        :rtype: int
        """

        term = self._write_termination if termination is None else termination
        enco = self._encoding if encoding is None else encoding

        if term:
            if message.endswith(term):
                warnings.warn("write message already ends with "
                              "termination characters", stacklevel=2)
            message += term

        count = self.write_raw(message.encode(enco))

        return count

    def read_raw(self, size=None):
        """Read the unmodified string sent from the instrument to the computer.

        In contrast to read(), no termination characters are stripped.

        :rtype: bytes
        """
        size = self.chunk_size if size is None else size

        ret = bytes()
        with warning_context("ignore", "VI_SUCCESS_MAX_CNT"):
            try:
                status = VI_SUCCESS_MAX_CNT
                while status == VI_SUCCESS_MAX_CNT:
                    logger.debug('%s - reading %d bytes (last status %r)',
                                 self._resource_name, size, status)
                    ret += self.visalib.read(self.session, size)
                    status = self.visalib.status
            except errors.VisaIOError as e:
                logger.debug('%s - exception while reading: %s', self._resource_name, e)
                raise

        return ret

    def read(self, termination=None, encoding=None):
        """Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting
        appropriate bus lines), or the termination characters sequence was
        detected.  Attention: Only the last character of the termination
        characters is really used to stop reading, however, the whole sequence
        is compared to the ending of the read string message.  If they don't
        match, a warning is issued.

        All line-ending characters are stripped from the end of the string.

        :rtype: str
        """
        enco = self._encoding if encoding is None else encoding

        if termination is None:
            termination = self._read_termination
            message = self.read_raw().decode(enco)
        else:
            with self.read_termination_context(termination):
                message = self.read_raw().decode(enco)

        if not termination:
            return message

        if not message.endswith(termination):
            warnings.warn("read string doesn't end with "
                          "termination characters", stacklevel=2)

        if self.__term_chars is None:
            return message.rstrip(CR + LF)

        return message[:-len(termination)]

    def read_values(self, fmt=None):
        """Read a list of floating point values from the device.

        :param fmt: the format of the values.  If given, it overrides
            the class attribute "values_format".  Possible values are bitwise
            disjunctions of the above constants ascii, single, double, and
            big_endian.  Default is ascii.

        :return: the list of read values
        :rtype: list
        """
        if not fmt:
            fmt = self.values_format

        if fmt & 0x01 == ascii:
            return parse_ascii(self.read())

        data = self.read_raw()

        try:
            if fmt & 0x03 == single:
                is_single = True
            elif fmt & 0x03 == double:
                is_single = False
            else:
                raise ValueError("unknown data values fmt requested")
            return parse_binary(data, fmt & 0x04 == big_endian, is_single)
        except ValueError as e:
            raise errors.InvalidBinaryFormat(e.args)

    def ask(self, message, delay=None):
        """A combination of write(message) and read()

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.ask_delay
        :returns: the answer from the device.
        :rtype: str
        """

        self.write(message)
        if delay is None:
            delay = self.ask_delay
        if delay > 0.0:
            time.sleep(delay)
        return self.read()

    def ask_for_values(self, message, format=None, delay=None):
        """A combination of write(message) and read_values()

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.ask_delay
        :returns: the answer from the device.
        :rtype: list
        """

        self.write(message)
        if delay is None:
            delay = self.ask_delay
        if delay > 0.0:
            time.sleep(delay)
        return self.read_values(format)

    def trigger(self):
        """Sends a software trigger to the device.
        """

        self.set_visa_attribute(VI_ATTR_TRIG_ID, VI_TRIG_SW)
        self.visalib.assert_trigger(self.session, VI_TRIG_PROT_DEFAULT)

    @property
    def term_chars(self):
        """Set or read a new termination character sequence (property).

        Normally, you just give the new termination sequence, which is appended
        to each write operation (unless it's already there), and expected as
        the ending mark during each read operation.  A typical example is CR+LF
        or just CR.  If you assign "" to this property, the termination
        sequence is deleted.

        The default is None, which means that CR + LF is appended to each write
        operation but not expected after each read operation (but stripped if
        present).
        """

        return self.__term_chars

    @term_chars.setter
    def term_chars(self, term_chars):

        # First, reset termination characters, in case something bad happens.
        self.__term_chars = ""

        if term_chars == "" or term_chars is None:
            self.read_termination = None
            self.write_termination = CR + LF
            self.__term_chars = None
            return
            # Only the last character in term_chars is the real low-level

        self.read_termination = term_chars
        self.write_termination = term_chars

    @term_chars.deleter
    def term_chars(self):
        self.term_chars = None

    @property
    def send_end(self):
        """Whether or not to assert EOI (or something equivalent after each
        write operation.
        """

        return self.get_visa_attribute(VI_ATTR_SEND_END_EN) == VI_TRUE

    @send_end.setter
    def send_end(self, send):
        self.set_visa_attribute(VI_ATTR_SEND_END_EN, VI_TRUE if send else VI_FALSE)

    @contextlib.contextmanager
    def read_termination_context(self, new_termination):
        term = self.get_visa_attribute(VI_ATTR_TERMCHAR)
        self.set_visa_attribute(VI_ATTR_TERMCHAR, ord(new_termination[-1]))
        yield
        self.set_visa_attribute(VI_ATTR_TERMCHAR, term)


class GpibInstrument(MessageBasedInstrument):
    """Class for GPIB instruments.

    This class extents the Instrument class with special operations and
    properties of GPIB instruments.

    :param gpib_identifier: strings are interpreted as instrument's VISA resource name.
                            Numbers are interpreted as GPIB number.
    :param board_number: the number of the GPIB bus.

    Further keyword arguments are passed to the constructor of class
    Instrument.

    """

    def __init__(self, gpib_identifier, board_number=0, resource_manager=None, **keyw):
        warn_for_invalid_kwargs(keyw, MessageBasedInstrument.ALL_KWARGS.keys())
        if isinstance(gpib_identifier, int):
            resource_name = "GPIB%d::%d" % (board_number, gpib_identifier)
        else:
            resource_name = gpib_identifier

        super(GpibInstrument, self).__init__(resource_name, resource_manager, **keyw)

        # Now check whether the instrument is really valid
        if self.interface_type != VI_INTF_GPIB:
            raise ValueError("device is not a GPIB instrument")

        self.visalib.enable_event(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

    def __del__(self):
        if self.session is not None:
            self.__switch_events_off()
            super(GpibInstrument, self).__del__()

    def __switch_events_off(self):
        self.visalib.disable_event(self.session, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)
        self.visalib.discard_events(self.session, VI_ALL_ENABLED_EVENTS, VI_ALL_MECH)

    def wait_for_srq(self, timeout=25):
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        :param timeout: the maximum waiting time in seconds.
                        Defaul: 25 (seconds).
                        None means waiting forever if necessary.
        """
        lib = self.visalib

        lib.enable_event(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

        if timeout and not(0 <= timeout <= 4294967):
            raise ValueError("timeout value is invalid")

        starting_time = time.clock()

        while True:
            if timeout is None:
                adjusted_timeout = VI_TMO_INFINITE
            else:
                adjusted_timeout = int((starting_time + timeout - time.clock()) * 1000)
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            event_type, context = lib.wait_on_event(self.session, VI_EVENT_SERVICE_REQ,
                                                    adjusted_timeout)
            lib.close(context)
            if self.stb & 0x40:
                break

        lib.discard_events(self.session, VI_EVENT_SERVICE_REQ, VI_QUEUE)

    @property
    def stb(self):
        """Service request status register."""

        return self.visalib.read_stb(self.session)

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


class SerialInstrument(MessageBasedInstrument):
    """Class for serial (RS232 or parallel port) instruments.  Not USB!

    This class extents the Instrument class with special operations and
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

    @property
    def baud_rate(self):
        """The baud rate of the serial instrument.
        """
        return self.get_visa_attribute(VI_ATTR_ASRL_BAUD)

    @baud_rate.setter
    def baud_rate(self, rate):
        self.set_visa_attribute(VI_ATTR_ASRL_BAUD, rate)

    @property
    def data_bits(self):
        """Number of data bits contained in each frame (from 5 to 8).
        """

        return self.get_visa_attribute(VI_ATTR_ASRL_DATA_BITS)

    @data_bits.setter
    def data_bits(self, bits):
        if not 5 <= bits <= 8:
            raise ValueError("number of data bits must be from 5 to 8")

        self.set_visa_attribute(VI_ATTR_ASRL_DATA_BITS, bits)

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


