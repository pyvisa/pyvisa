# -*- coding: utf-8 -*-
"""
    pyvisa.resources.registerbased
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for RegisterBased Instruments.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

from .resource import Resource


class RegisterBasedResource(Resource):
    """Base class for resources that use register based communication.
    """

    def read_memory(self, space, offset, width, extended=False):
        """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory.

        Corresponds to viIn* functions of the visa library.
        """
        return self.visalib.read_memory(self.session, space, offset, width, extended)

    def write_memory(self, space, offset, data, width, extended=False):
        """Write in an 8-bit, 16-bit, 32-bit, value to the specified memory space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.

        Corresponds to viOut* functions of the visa library.
        """
        return self.visalib.write_memory(self.session, space, offset, data, width, extended)

    def move_in(self, space, offset, length, width, extended=False):
        """Moves a block of data to local memory from the specified address space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        """
        return self.visalib.move_in(self.session, space, offset, length, width, extended)

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
        return self.visalib.move_out(space, offset, length, data, width, extended)
