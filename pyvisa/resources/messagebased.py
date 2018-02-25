# -*- coding: utf-8 -*-
"""
    pyvisa.resources.messagebased
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for MessageBased Instruments.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import contextlib
import time
import warnings

from .. import logger
from .. import constants
from .. import errors
from .. import util

from .resource import Resource


class ControlRenMixin(object):
    """Common control_ren method of some messaged based resources.

    """
    # It should work for GPIB, USB and some TCPIP
    # For TCPIP I found some (all?) NI's VISA library do not handle
    # control_ren, but it works for Agilent's VISA library (at least some of
    # them)
    def control_ren(self, mode):
        """Controls the state of the GPIB Remote Enable (REN) interface line,
        and optionally the remote/local state of the device.

        Corresponds to viGpibControlREN function of the VISA library.

        :param mode: Specifies the state of the REN line and optionally the
                     device remote/local state. (Constants.GPIB_REN*)
        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.gpib_control_ren(self.session, mode)


class MessageBasedResource(Resource):
    """Base class for resources that use message based communication.
    """

    CR = '\r'
    LF = '\n'

    _read_termination = None
    _write_termination = CR + LF
    _encoding = 'ascii'

    chunk_size = 20 * 1024
    query_delay = 0.0

    _values_format = None

    def __init__(self, *args, **kwargs):
        super(MessageBasedResource, self).__init__(*args, **kwargs)

    @property
    def encoding(self):
        """Encoding used for read and write operations.
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        # Test that the encoding specified makes sense.
        'test encoding'.encode(encoding).decode(encoding)
        self._encoding = encoding

    @property
    def read_termination(self):
        """Read termination character.
        """
        return self._read_termination

    @read_termination.setter
    def read_termination(self, value):

        if value:
            # termination character, the rest is just used for verification
            # after each read operation.
            last_char = value[-1:]
            # Consequently, it's illogical to have the real termination
            # character twice in the sequence (otherwise reading would stop
            # prematurely).

            if last_char in value[:-1]:
                raise ValueError("ambiguous ending in termination characters")

            self.set_visa_attribute(constants.VI_ATTR_TERMCHAR, ord(last_char))
            self.set_visa_attribute(constants.VI_ATTR_TERMCHAR_EN,
                                    constants.VI_TRUE)
        else:
            # The termchar is also used in VI_ATTR_ASRL_END_IN (for serial
            # termination) so return it to its default.
            self.set_visa_attribute(constants.VI_ATTR_TERMCHAR, ord(self.LF))
            self.set_visa_attribute(constants.VI_ATTR_TERMCHAR_EN,
                                    constants.VI_FALSE)

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

    def write_ascii_values(self, message, values, converter='f', separator=',',
                           termination=None, encoding=None):
        """Write a string message to the device followed by values in ascii
        format.

        The write_termination is always appended to it.

        :param message: the message to be sent.
        :type message: unicode (Py2) or str (Py3)
        :param values: data to be writen to the device.
        :param converter: function used to convert each value.
                          String formatting codes are also accepted.
                          Defaults to str.
        :type converter: callable | str
        :param separator: a callable that join the values in a single str.
                          If a str is given, separator.join(values) is used.
        :type: separator: (collections.Iterable[T]) -> str | str
        :return: number of bytes written.
        :rtype: int
        """

        term = self._write_termination if termination is None else termination
        enco = self._encoding if encoding is None else encoding

        if term and message.endswith(term):
                warnings.warn("write message already ends with "
                              "termination characters", stacklevel=2)

        block = util.to_ascii_block(values, converter, separator)

        message = message.encode(enco) + block.encode(enco)

        if term:
            message += term.encode(enco)

        count = self.write_raw(message)

        return count

    def write_binary_values(self, message, values, datatype='f',
                            is_big_endian=False, termination=None,
                            encoding=None):
        """Write a string message to the device followed by values in binary
        format.

        The write_termination is always appended to it.

        :param message: the message to be sent.
        :type message: unicode (Py2) or str (Py3)
        :param values: data to be writen to the device.
        :param datatype: the format string for a single element. See struct
                         module.
        :param is_big_endian: boolean indicating endianess.
        :return: number of bytes written.
        :rtype: int
        """
        term = self._write_termination if termination is None else termination
        enco = self._encoding if encoding is None else encoding

        if term and message.endswith(term):
                warnings.warn("write message already ends with "
                              "termination characters", stacklevel=2)

        block = util.to_ieee_block(values, datatype, is_big_endian)

        message = message.encode(enco) + block

        if term:
            message += term.encode(enco)

        count = self.write_raw(message)

        return count

    def read_bytes(self, count, chunk_size=None, break_on_termchar=False):
        """Read a certain number of bytes from the instrument.

        :param count: The number of bytes to read from the instrument.
        :type count: int
        :param chunk_size: The chunk size to use to perform the reading.
        :type chunk_size: int
        :param break_on_termchar: Should the reading stop when a termination
            character is encountered.
        :type brak_on_termchar: bool

        :rtype: bytes

        """
        chunk_size = chunk_size or self.chunk_size
        ret = bytearray()
        left_to_read = count
        termchar_read = constants.StatusCode.success_termination_character_read

        with self.ignore_warning(constants.VI_SUCCESS_DEV_NPRESENT,
                                 constants.VI_SUCCESS_MAX_CNT):
            try:
                status = None
                while len(ret) < count:
                    size = min(chunk_size, left_to_read)
                    logger.debug('%s - reading %d bytes (last status %r)',
                                 self._resource_name, size, status)
                    chunk, status = self.visalib.read(self.session, size)
                    ret.extend(chunk)
                    left_to_read -= len(chunk)
                    if break_on_termchar and status == termchar_read:
                        break
            except errors.VisaIOError as e:
                logger.debug('%s - exception while reading: %s\n'
                             'Buffer content: %r',  self._resource_name, e,
                             ret)
                raise
        return bytes(ret)

    def read_raw(self, size=None):
        """Read the unmodified string sent from the instrument to the computer.

        In contrast to read(), no termination characters are stripped.

        :param size: The chunk size to use when reading the data.

        :rtype: bytes
        """
        return bytes(self._read_raw(size))

    def _read_raw(self, size=None):
        """Read the unmodified string sent from the instrument to the computer.

        In contrast to read(), no termination characters are stripped.

        :param size: The chunk size to use when reading the data.

        :rtype: bytearray
        """
        size = self.chunk_size if size is None else size

        loop_status = constants.StatusCode.success_max_count_read

        ret = bytearray()
        with self.ignore_warning(constants.VI_SUCCESS_DEV_NPRESENT,
                                 constants.VI_SUCCESS_MAX_CNT):
            try:
                status = loop_status
                while status == loop_status:
                    logger.debug('%s - reading %d bytes (last status %r)',
                                 self._resource_name, size, status)
                    chunk, status = self.visalib.read(self.session, size)
                    ret.extend(chunk)
            except errors.VisaIOError as e:
                logger.debug('%s - exception while reading: %s\nBuffer '
                             'content: %r', self._resource_name, e, ret)
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
            message = self._read_raw().decode(enco)
        else:
            with self.read_termination_context(termination):
                message = self._read_raw().decode(enco)

        if not termination:
            return message

        if not message.endswith(termination):
            warnings.warn("read string doesn't end with "
                          "termination characters", stacklevel=2)

        return message[:-len(termination)]

    def read_ascii_values(self, converter='f', separator=',', container=list,
                          delay=None):
        """Read values from the device in ascii format returning an iterable of
        values.

        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.query_delay
        :param converter: function used to convert each element.
                          Defaults to float
        :type converter: callable
        :param separator: a callable that split the str into individual
                          elements. If a str is given, data.split(separator) is
                          used.
        :type: separator: (str) -> collections.Iterable[int] | str
        :param container: container type to use for the output data.
        :returns: the answer from the device.
        :rtype: list

        """
        # Use read rather than _read_raw because we cannot handle a bytearray
        block = self.read()

        return util.from_ascii_block(block, converter, separator, container)

    def read_binary_values(self, datatype='f', is_big_endian=False,
                           container=list, header_fmt='ieee'):
        """Read values from the device in binary format returning an iterable
        of values.

        :param datatype: the format string for a single element. See struct
                         module.
        :param is_big_endian: boolean indicating endianess.
                              Defaults to False.
        :param container: container type to use for the output data.
        :param header_fmt: format of the header prefixing the data. Possible
                           values are: 'ieee', 'hp', 'empty'
        :returns: the answer from the device.
        :rtype: type(container)

        """
        block = self._read_raw()
        expected_length = 0

        if header_fmt == 'ieee':
            offset, data_length = util.parse_ieee_block_header(block)
            expected_length = offset + data_length
        elif header_fmt == 'hp':
            offset, data_length = util.parse_hp_block_header(block,
                                                             is_big_endian)
            expected_length = offset + data_length

        if self._read_termination is not None:
            expected_length += len(self._read_termination)

        while len(block) < expected_length:
            block.extend(self._read_raw())

        try:
            if header_fmt == 'ieee':
                return util.from_ieee_block(block, datatype, is_big_endian,
                                            container)
            elif header_fmt == 'hp':
                return util.from_hp_block(block, datatype, is_big_endian,
                                          container)
            elif header_fmt == 'empty':
                return util.from_binary_block(block, 0, None, datatype,
                                              is_big_endian, container)
            else:
                raise
        except ValueError as e:
            raise errors.InvalidBinaryFormat(e.args)

    def query(self, message, delay=None):
        """A combination of write(message) and read()

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.query_delay
        :returns: the answer from the device.
        :rtype: str
        """

        self.write(message)

        delay = self.query_delay if delay is None else delay

        if delay > 0.0:
            time.sleep(delay)
        return self.read()

    def query_ascii_values(self, message, converter='f', separator=',',
                           container=list, delay=None):
        """Query the device for values in ascii format returning an iterable of
        values.

        :param message: the message to send.
        :type message: str
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.query_delay
        :param converter: function used to convert each element.
                          Defaults to float
        :type converter: callable
        :param separator: a callable that split the str into individual
                          elements. If a str is given, data.split(separator) is
                          used.
        :type: separator: (str) -> collections.Iterable[int] | str
        :param container: container type to use for the output data.
        :returns: the answer from the device.
        :rtype: list
        """

        self.write(message)
        if delay is None:
            delay = self.query_delay
        if delay > 0.0:
            time.sleep(delay)

        return self.read_ascii_values(converter, separator, container,
                                      delay)

    def query_binary_values(self, message, datatype='f', is_big_endian=False,
                            container=list, delay=None, header_fmt='ieee'):
        """Query the device for values in binary format returning an iterable
        of values.

        :param message: the message to send to the instrument.
        :param datatype: the format string for a single element. See struct
                         module.
        :param is_big_endian: boolean indicating endianess.
                              Defaults to False.
        :param container: container type to use for the output data.
        :param delay: delay in seconds between write and read operations.
                      if None, defaults to self.query_delay
        :returns: the answer from the device.
        :rtype: list
        """
        if header_fmt not in ('ieee', 'empty', 'hp'):
            raise ValueError("Invalid header format. Valid options are 'ieee',"
                             " 'empty', 'hp'")

        self.write(message)
        if delay is None:
            delay = self.query_delay
        if delay > 0.0:
            time.sleep(delay)

        return self.read_binary_values(datatype, is_big_endian, container,
                                       header_fmt)

    def assert_trigger(self):
        """Sends a software trigger to the device.
        """

        self.visalib.assert_trigger(self.session,
                                    constants.VI_TRIG_PROT_DEFAULT)

    @property
    def stb(self):
        """Service request status register."""

        return self.read_stb()

    def read_stb(self):
        """Service request status register.
        """
        value, retcode = self.visalib.read_stb(self.session)
        return value

    @contextlib.contextmanager
    def read_termination_context(self, new_termination):
        term = self.get_visa_attribute(constants.VI_ATTR_TERMCHAR)
        self.set_visa_attribute(constants.VI_ATTR_TERMCHAR,
                                ord(new_termination[-1]))
        yield
        self.set_visa_attribute(constants.VI_ATTR_TERMCHAR, term)


# Rohde and Schwarz Device via Passport. Not sure which Resource should be.
MessageBasedResource.register(constants.InterfaceType.rsnrp,
                              'INSTR')(MessageBasedResource)
