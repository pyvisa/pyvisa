# -*- coding: utf-8 -*-
"""
    pyvisa.resources.registerbased
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for RegisterBased Instruments.

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


class RegisterBasedResource(Resource):
    """Class for RegisterBased Resource all kinds of Instruments.


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

    allow_dma = boolean_property(VI_ATTR_DMA_ALLOW_EN,
                                 doc='This attribute specifies whether I/O accesses should '
                                     'use DMA (True) or Programmed I/O (False).')

    destination_increment = range_property(VI_ATTR_DEST_INCREMENT, 0, 1,
                                           doc='Used in the viMoveOutXX() operations to specify by how many '
                                               'elements the destination offset is to be incremented after '
                                               'every transfer. Default is 1')

    source_increment = range_property(VI_ATTR_SRC_INCREMENT, 0, 1,
                                      doc='Used in the viMoveOutXX() operations to specify by how many '
                                          'elements the destination offset is to be incremented after '
                                          'every transfer. Default is 1')

    def read_memory(self, space, offset, width, extended=False):
        """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory.

        Corresponds to viIn* functions of the visa library.
        """
        return self._visalib.read_memory(self.session, space, offset, width, extended)

    def write_memory(self, space, offset, data, width, extended=False):
        """Write in an 8-bit, 16-bit, 32-bit, value to the specified memory space and offset.


        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.

        Corresponds to viOut* functions of the visa library.
        """
        return self._visalib.write_memory(self.session, space, offset, width, extended)

    def move_in(self, space, offset, length, width, extended=False):
        """Moves a block of data to local memory from the specified address space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        """
        return self._visalib.move_in(self.session, space, offset, width, extended)

    def move_out(self, space, offset, length, data, width, extended=False):
        """Moves a block of data from local memory to the specified address space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        """
        return self._visalib.move_out(space, offset, length, data, width, extended)
