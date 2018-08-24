# -*- coding: utf-8 -*-
"""
    pyvisa.resources.usb
    ~~~~~~~~~~~~~~~~~~~~

    High level wrapper for USB resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import
import warnings

from .. import constants
from .messagebased import MessageBasedResource, ControlRenMixin


@MessageBasedResource.register(constants.InterfaceType.usb, 'INSTR')
class USBInstrument(ControlRenMixin, MessageBasedResource):
    """Communicates with devices of type USB::manufacturer ID::model code::serial number

    More complex resource names can be specified with the following grammar:
        USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    def control_in(self, request_type_bitmap_field, request_id, request_value, index, length=0):
        """Performs a USB control pipe transfer from the device.

        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param length: wLength parameter of the setup stage of a USB control transfer.
                       This value also specifies the size of the data buffer to receive the data from the
                       optional data stage of the control transfer.
        :return: The data buffer that receives the data from the optional data stage of the control transfer.
        :rtype: bytes
        """
        return self.visalib.usb_control_in(self.session, request_type_bitmap_field,
                                           request_id, request_value, index, length)

    def control_out(self, request_type_bitmap_field, request_id, request_value, index, data=""):
        """Performs a USB control pipe transfer to the device.

        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param data: The data buffer that sends the data in the optional data stage of the control transfer.
        """
        return self.visalib.usb_control_out(self.session, request_type_bitmap_field, 
                                            request_id, request_value, index, data)

    def usb_control_out(self, request_type_bitmap_field, request_id, request_value, index, data=""):
        """Performs a USB control pipe transfer to the device. (Deprecated)

        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param data: The data buffer that sends the data in the optional data stage of the control transfer.
        """
        warnings.warn('usb_control_out is deprecated use control_out instead.', FutureWarning)
        return self.control_out(request_type_bitmap_field, request_id, request_value, index, data)


@MessageBasedResource.register(constants.InterfaceType.usb, 'RAW')
class USBRaw(MessageBasedResource):
    """Communicates with to devices of type USB::manufacturer ID::model code::serial number::RAW

    More complex resource names can be specified with the following grammar:
        USB[board]::manufacturer ID::model code::serial number[::USB interface number]::RAW

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """
