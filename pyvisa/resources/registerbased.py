# -*- coding: utf-8 -*-
"""
    pyvisa.resources.registerbased
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for RegisterBased Instruments.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Iterable, List

from .. import constants
from .resource import Resource


class RegisterBasedResource(Resource):
    """Base class for resources that use register based communication.
    """

    def read_memory(
        self,
        space: constants.AddressSpace,
        offset: int,
        width: constants.DataWidth,
        extended: bool = False,
    ) -> int:
        """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory.

        Corresponds to viIn* functions of the visa library.
        """
        return self.visalib.read_memory(self.session, space, offset, width, extended)[0]

    def write_memory(
        self,
        space: constants.AddressSpace,
        offset: int,
        data: int,
        width: constants.DataWidth,
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 8-bit, 16-bit, 32-bit, value to the specified memory space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.

        Corresponds to viOut* functions of the visa library.
        """
        return self.visalib.write_memory(
            self.session, space, offset, data, width, extended
        )

    def move_in(
        self,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        width: constants.DataWidth,
        extended: bool = False,
    ) -> List[int]:
        """Moves a block of data to local memory from the specified address space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        """
        return self.visalib.move_in(
            self.session, space, offset, length, width, extended
        )[0]

    def move_out(
        self,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        width: constants.DataWidth,
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves a block of data from local memory to the specified address space and offset.

        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        """
        return self.visalib.move_out(
            self.session, space, offset, length, data, width, extended
        )
