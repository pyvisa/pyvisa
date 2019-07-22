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
import sys

if sys.version_info > (3,2):
    perf_counter = time.perf_counter
else:
    perf_counter = time.clock

from .. import constants
from .resource import Resource
from .messagebased import MessageBasedResource, ControlRenMixin


class _GPIBMixin(ControlRenMixin):
    """Common attributes and methods of GPIB Instr and Interface.
    """

    def send_command(self, data):
        """Write GPIB command bytes on the bus.

        Corresponds to viGpibCommand function of the VISA library.

        :param data: data tor write.
        :type data: bytes
        :return: Number of written bytes, return value of the library call.
        :rtype: int, VISAStatus
        """
        return self.visalib.gpib_command(self.session, data)

    def control_atn(self, mode):
        """Specifies the state of the ATN line and the local active controller state.

        Corresponds to viGpibControlATN function of the VISA library.

        :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                     (Constants.GPIB_ATN*)
        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.gpib_control_atn(self.session, mode)

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
        return self.visalib.gpib_pass_control(self.session, primary_address, secondary_address)

    def send_ifc(self):
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        Corresponds to viGpibSendIFC function of the VISA library.

        :return: return value of the library call.
        :rtype: VISAStatus
        """
        return self.visalib.gpib_send_ifc(self.session)


@Resource.register(constants.InterfaceType.gpib, 'INSTR')
class GPIBInstrument(_GPIBMixin, MessageBasedResource):
    """Communicates with to devices of type GPIB::<primary address>[::INSTR]

    More complex resource names can be specified with the following grammar:
        GPIB[board]::primary address[::secondary address][::INSTR]

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    def wait_for_srq(self, timeout=25000):
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        :param timeout: the maximum waiting time in milliseconds.
                        Defaul: 25000 (milliseconds).
                        None means waiting forever if necessary.
        """
        self.enable_event(constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)

        if timeout and not(0 <= timeout <= 4294967295):
            raise ValueError("timeout value is invalid")

        starting_time = perf_counter()

        while True:
            if timeout is None:
                adjusted_timeout = constants.VI_TMO_INFINITE
            else:
                adjusted_timeout = int((starting_time +
                                        timeout/1e3 -
                                        perf_counter())*1e3)
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            self.wait_on_event(constants.VI_EVENT_SERVICE_REQ, adjusted_timeout)
            if self.stb & 0x40:
                break

        self.discard_events(constants.VI_EVENT_SERVICE_REQ, constants.VI_QUEUE)


@Resource.register(constants.InterfaceType.gpib, 'INTFC')
class GPIBInterface(_GPIBMixin, Resource):
    """Communicates with to devices of type GPIB::INTFC

    More complex resource names can be specified with the following grammar:
        GPIB[board]::INTFC

    Do not instantiate directly, use :meth:`pyvisa.highlevel.ResourceManager.open_resource`.
    """

    def group_execute_trigger(self, *resources):

        for resource in resources:
            if not isinstance(resource, GPIBInstrument):
                raise ValueError('%r is not a GPIBInstrument', resource)

            # TODO: check that all resources are in the same board.

        if not self.is_controller_in_charge:
            self.send_ifc()

        command = [0x40, 0x20+31, ] # broadcast TAD#0 and "UNL" (don't listen) to all devices

        for resource in resources:
            # tell device GPIB::11 to listen
            command.append(0x20 + resource.primary_address)

        # send GET ('group execute trigger')
        command.append(0x08)

        return self.send_command(bytes(command))

    def flush(self, mask):
        """Manually clears the specified buffers.

        Depending on the mask this can cause the buffer data to be written to
        the device.

        :param mask: Specifies the action to be taken with flushing the buffer.
            See highlevel.VisaLibraryBase.flush for a detailed description.

        """
        self.visalib.flush(self.session, mask)
