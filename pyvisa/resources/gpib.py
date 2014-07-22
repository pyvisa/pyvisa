# -*- coding: utf-8 -*-
"""
    pyvisa.resources.gpib
    ~~~~~~~~~~~~~~~~~~~~~

    High level wrapper for GPIB resources.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import time

from .. import constants
from .resource import Resource
from .messagebased import MessageBasedResource
from . import helpers as hlp


class _GPIBMixin(object):
    """Common attributes and methods of GPIB Instr and Interface.
    """

    visalib = None
    session = None

    allow_dma = hlp.boolean_attr('VI_ATTR_DMA_ALLOW_EN',
                                 doc='This attribute specifies whether I/O accesses should '
                                     'use DMA (True) or Programmed I/O (False).')

    primary_address = hlp.attr('VI_ATTR_GPIB_PRIMARY_ADDR',
                               doc='Specifies the primary address of the GPIB device used by the given session.',
                               ro=True)

    remote_enabled = hlp.enum_attr('VI_ATTR_GPIB_REN_STATE', constants.LineState,
                                   doc='Returns the current state of the GPIB REN (Remote ENable) interface line.',
                                   ro=True)

    secondary_address = hlp.attr('VI_ATTR_GPIB_SECONDARY_ADDR',
                                 doc='Specifies the secondary address of the GPIB device used by the given session.',
                                 ro=True)

    def assert_trigger(self):
        """Sends a software trigger to the device.
        """

        self.visalib.assert_trigger(self.session, constants.VI_TRIG_PROT_DEFAULT)

    def send_command(self, data):
        """Write GPIB command bytes on the bus.

        Corresponds to viGpibCommand function of the VISA library.

        :param data: data tor write.
        :type data: bytes
        :return: Number of written bytes, return value of the library call.
        :rtype: int, VISAStatus
        """
        return self.visalib.viGpibCommand(self.session, data, data)

    def control_atn(self, mode):
        """Specifies the state of the ATN line and the local active controller state.

        Corresponds to viGpibControlATN function of the VISA library.

        :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                     (Constants.GPIB_ATN*)
        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.viGpibControlATN(self.session, mode)

    def control_ren(self, mode):
        """Controls the state of the GPIB Remote Enable (REN) interface line, and optionally the remote/local
        state of the device.

        Corresponds to viGpibControlREN function of the VISA library.

        :param mode: Specifies the state of the REN line and optionally the device remote/local state.
                     (Constants.GPIB_REN*)
        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.viGpibControlREN(self.session, mode)

    def pass_control(self, primary_address, secondary_address):
        """Tell the GPIB device at the specified address to become controller in charge (CIC).

        Corresponds to viGpibPassControl function of the VISA library.

        :param primary_address: Primary address of the GPIB device to which you want to pass control.
        :param secondary_address: Secondary address of the targeted GPIB device.
                                  If the targeted device does not have a secondary address,
                                  this parameter should contain the value Constants.NO_SEC_ADDR.
        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.viGpibPassControl(self.session, primary_address, secondary_address)

    def send_ifc(self):
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        Corresponds to viGpibSendIFC function of the VISA library.

        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.viGpibSendIFC(self.session)


@Resource.register(constants.InterfaceType.gpib, 'INSTR')
class GPIBInstrument(_GPIBMixin, MessageBasedResource):
    """Communicates with to devices of type GPIB::<primary address>[::INSTR]

    More complex resource names can be specified with the following grammar:
        GPIB[board]::primary address[::secondary address][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open`.
    """

    def before_close(self):
        self.__switch_events_off()
        super(GPIBInstrument, self).before_close()

    def __switch_events_off(self):
        self.visalib.disable_event(self.session, constants.VI_ALL_ENABLED_EVENTS, constants.VI_ALL_MECH)
        self.visalib.discard_events(self.session, constants.VI_ALL_ENABLED_EVENTS, constants.VI_ALL_MECH)

    enable_repeat_addressing = hlp.boolean_attr('VI_ATTR_GPIB_READDR_EN',
                                                doc='Specifies whether to use repeat addressing '
                                                    'before each read or write operation.')

    enable_unaddressing = hlp.boolean_attr('VI_ATTR_GPIB_UNADDR_EN',
                                           doc='Specifies whether to unaddress the device (UNT and UNL) '
                                               'after each read or write operation.')

    def wait_for_srq(self, timeout=25000):
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        :param timeout: the maximum waiting time in milliseconds.
                        Defaul: 25000 (seconds).
                        None means waiting forever if necessary.
        """
        lib = self.visalib

        lib.enable_event(self.session, constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)

        if timeout and not(0 <= timeout <= 4294967295):
            raise ValueError("timeout value is invalid")

        starting_time = time.clock()

        while True:
            if timeout is None:
                adjusted_timeout = constants.VI_TMO_INFINITE
            else:
                adjusted_timeout = int((starting_time + timeout - time.clock()))
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            event_type, context = lib.wait_on_event(self.session, constants.VI_EVENT_SERVICE_REQ,
                                                    adjusted_timeout)
            lib.close(context)
            if self.stb & 0x40:
                break

        lib.discard_events(self.session, constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)


@Resource.register(constants.InterfaceType.gpib, 'INTFC')
class GPIBInterface(_GPIBMixin, Resource):
    """Communicates with to devices of type GPIB::INTFC

    More complex resource names can be specified with the following grammar:
        GPIB[board]::INTFC

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open`.
    """

    address_state = hlp.enum_attr('VI_ATTR_GPIB_ADDR_STATE', constants.AddressState,
                                  'Shows whether the specified GPIB interface is currently addressed to talk or listen, or is not addressed.',
                                  ro=True)

    atn_state = hlp.enum_attr('VI_ATTR_GPIB_ATN_STATE', constants.LineState,
                              'Shows the current state of the GPIB ATN (ATtentioN) interface line.',
                              ro=True)

    is_controller_in_charge = hlp.boolean_attr('VI_ATTR_GPIB_CIC_STATE',
                                               'Shows whether the specified GPIB interface is currently CIC (Controller In Charge).',
                                               ro=True)

    is_system_controller = hlp.boolean_attr('VI_ATTR_GPIB_SYS_CNTRL_STATE',
                                            'Shows whether the specified GPIB interface is currently the system controller.\n\n'
                                            'In some implementations, this attribute may be modified only through a configuration utility.',
                                            ro=True)
    ndac_state = hlp.enum_attr('VI_ATTR_GPIB_NDAC_STATE', constants.LineState,
                               'Shows the current state of the GPIB NDAC (Not Data ACcepted) interface line.',
                               ro=True)
