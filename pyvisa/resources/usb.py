# -*- coding: utf-8 -*-
"""
    pyvisa.resources.gpib
    ~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for Serial resources.

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

from .messagebased import MessageBasedResource
from .helpers import range_property


class USBResource(MessageBasedResource):
    """Class for GPIB Resources.

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

    is_4882_compliant = boolean_property(VI_ATTR_4882_COMPLIANT,
                                         doc='Specifies whether the device is 488.2 compliant.',
                                         ro=True)

    manufacturer_id = attr_property(VI_ATTR_MANF_ID,
                                    doc='Return the Vendor ID',
                                    ro=True)

    manufacturer_name = attr_property(VI_ATTR_MANF_NAME,
                                      doc='Return the Vendor Name',
                                      ro=True)

    maximum_interrupt_size = range_property(VI_ATTR_USB_MAX_INTR_SIZE, 0, 256,
                                            doc='Specifies the maximum size of data that will be stored '
                                                'by any given USB interrupt. If a USB interrupt contains '
                                                'more data than this size, the data in excess of this size '
                                                'will be lost.')

    model_code = attr_property(VI_ATTR_MODEL_CODE,
                               doc='Return the Product ID')


    model_name = attr_property(VI_ATTR_MODEL_NAME,
                               doc='Return the Product Name')

    interface_number = attr_property(VI_ATTR_USB_INTFC_NUM,
                                     doc='Specifies the USB interface number used by the given session.',
                                     ro=True)

    usb_protocol = attr_property(VI_ATTR_USB_PROTOCOL,
                                 doc='Specifies the USB protocol used by this USB interface.',
                                 ro=True)

    serial_number = attr_property(VI_ATTR_USB_SERIAL_NUM,
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
        return self._visalib.usb_control_in(self.session, request_type_bitmap_field,
                                            request_id, request_value, index, length)

    def usb_control_out(request_type_bitmap_field, request_id, request_value, index, data=""):
        """Performs a USB control pipe transfer to the device.

        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param data: The data buffer that sends the data in the optional data stage of the control transfer.
        """
        return self._visalib.usb_control_out(request_type_bitmap_field, request_id, request_value, index, data)



