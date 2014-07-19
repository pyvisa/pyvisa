# -*- coding: utf-8 -*-
"""
    pyvisa.resources.messagebased
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for MessageBased Instruments.

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
    :param buffer_size: size of data packets in bytes that are read from the
                       device.
    :param lock: whether you want to have exclusive access to the device.
                 Default: VI_NO_LOCK
    :param ask_delay: waiting time in seconds after each write command.
                      Default: 0.0
    :param send_end: whether to assert end line after each write command.
                     Default: True
    :param values_format: floating point data value format. Default: ascii (0)
    """

    DEFAULT_KWARGS = {'read_termination': None,
                      'write_termination': CR + LF,
                      #: Size in bytes for read or write operations.
                      'buffer_size': 20 * 1024,
                      #: Seconds to wait between write and read operations inside ask.
                      'ask_delay': 0.0,
                      #: Indicates
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
    def io_protocol(self):
        """I/O protocol for the current hardware interface.

        Valid values: VI_PROT*

        Default is VI_PROT_NORMAL meaning the default protocols for the given interface.
        """
        self.get_visa_attribute(VI_ATTR_IO_PROT)

    @io_protocol.setter
    def io_protocol(self, value):
        self.set_visa_attribute(VI_ATTR_IO_PROT, value)

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
        """Write a byte message to the device.

        :param message: the message to be sent.
        :type message: bytes
        :return: number of bytes written.
        :rtype: int
        """
        return self.visalib.write(self.session, message)

    def write(self, message, termination=None, encoding=None):
        """Write a string message to the device.

        The write_termination is always appended to it.

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

        self._visalib.assert_trigger(self.session, VI_TRIG_PROT_DEFAULT)

    @property
    def stb(self):
        """Service request status register."""

        return self._visalib.read_stb(self.session)

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
