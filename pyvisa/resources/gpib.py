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


class GpibResource(MessageBasedResource):
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

    allow_dma = boolean_property(VI_ATTR_DMA_ALLOW_EN,
                                 doc='This attribute specifies whether I/O accesses should '
                                     'use DMA (True) or Programmed I/O (False).')

    primary_address = attr_property(VI_ATTR_GPIB_PRIMARY_ADDR,
                                    doc='Specifies the primary address of the GPIB device used by the given session.',
                                    ro=True)

    enable_repeat_addressing = boolean_property(VI_ATTR_GPIB_READDR_EN,
                                                doc='Specifies whether to use repeat addressing '
                                                    'before each read or write operation.')

    remote_enabled = enum_property(VI_ATTR_GPIB_REN_STATE, contants.LineState,
                                   doc='Returns the current state of the GPIB REN (Remote ENable) interface line.',
                                   ro=True)

    primary_address = attr_property(VI_ATTR_GPIB_SECONDARY_ADDR,
                                    doc='Specifies the secondary address of the GPIB device used by the given session.',
                                    ro=True)

    enable_unaddressing = boolean_property(VI_ATTR_GPIB_UNADDR_EN,
                                           doc='Specifies whether to unaddress the device (UNT and UNL) '
                                               'after each read or write operation.')

    def remote_mode(self, mode):
        """Controls the state of the GPIB Remote Enable (REN) interface line,
        and optionally the remote/local state of the device.

        :param mode: Specifies the state of the REN line and optionally
                     the device remote/local state. See values VI_GPIB_REN_*
        """
        self._visalib.gpib_control_ren(mode)

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


