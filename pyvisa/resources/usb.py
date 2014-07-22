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

from .. import constants
from .messagebased import MessageBasedResource
from . import helpers as hlp


@MessageBasedResource.register(constants.InterfaceType.usb, 'INSTR')
class USBInstrument(MessageBasedResource):
    """Communicates with devices of type USB::manufacturer ID::model code::serial number

    More complex resource names can be specified with the following grammar:
        USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open`.
    """

    is_4882_compliant = hlp.boolean_attr('VI_ATTR_4882_COMPLIANT',
                                         doc='Specifies whether the device is 488.2 compliant.',
                                         ro=True)

    manufacturer_id = hlp.attr('VI_ATTR_MANF_ID',
                               doc='Return the Vendor ID',
                               ro=True)

    manufacturer_name = hlp.attr('VI_ATTR_MANF_NAME',
                                 doc='Return the Vendor Name',
                                 ro=True)

    _d_ = 'Specifies the maximum size of data that will be stored by any given USB interrupt\n\n' \
          'If a USB interrupt contains more data than this size, the data in excess of this size ' \
          'will be lost.'
    maximum_interrupt_size = hlp.range_attr('VI_ATTR_USB_MAX_INTR_SIZE', 0, 256, _d_)

    del _d_

    model_code = hlp.attr('VI_ATTR_MODEL_CODE',
                          doc='Return the Product ID')

    model_name = hlp.attr('VI_ATTR_MODEL_NAME',
                          doc='Return the Product Name')

    interface_number = hlp.attr('VI_ATTR_USB_INTFC_NUM',
                                doc='Specifies the USB interface number used by the given session.',
                                ro=True)

    usb_protocol = hlp.attr('VI_ATTR_USB_PROTOCOL',
                            doc='Specifies the USB protocol used by this USB interface.',
                            ro=True)

    serial_number = hlp.attr('VI_ATTR_USB_SERIAL_NUM',
                             doc='Specifies the USB serial number of this device.',
                             ro=True)

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

    def usb_control_out(self, request_type_bitmap_field, request_id, request_value, index, data=""):
        """Performs a USB control pipe transfer to the device.

        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param data: The data buffer that sends the data in the optional data stage of the control transfer.
        """
        return self.visalib.usb_control_out(request_type_bitmap_field, request_id, request_value, index, data)


@MessageBasedResource.register(constants.InterfaceType.usb, 'RAW')
class USBRaw(MessageBasedResource):
    """Communicates with to devices of type USB::manufacturer ID::model code::serial number::RAW

    More complex resource names can be specified with the following grammar:
        USB[board]::manufacturer ID::model code::serial number[::USB interface number]::RAW

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open`.
    """
