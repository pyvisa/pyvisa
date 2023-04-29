# -*- coding: utf-8 -*-
"""High level wrapper for GPIB resources.

This file is part of PyVISA.

:copyright: 2014-2022 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
from time import perf_counter
from typing import Tuple

from .. import attributes, constants
from ..attributes import Attribute
from .messagebased import ControlRenMixin, MessageBasedResource
from .resource import Resource


class _GPIBMixin(ControlRenMixin):
    """Common attributes and methods of GPIB Instr and Interface."""

    #: Primary address of the GPIB device used by the given session.
    primary_address: Attribute[int] = attributes.AttrVI_ATTR_GPIB_PRIMARY_ADDR()

    #: Secondary address of the GPIB device used by the given session.
    secondary_address: Attribute[int] = attributes.AttrVI_ATTR_GPIB_SECONDARY_ADDR()

    #: Current state of the GPIB REN (Remote ENable) interface line.
    remote_enabled: Attribute[
        constants.LineState
    ] = attributes.AttrVI_ATTR_GPIB_REN_STATE()


@Resource.register(constants.InterfaceType.gpib, "INSTR")
class GPIBInstrument(_GPIBMixin, MessageBasedResource):
    """Communicates with to devices of type GPIB::<primary address>[::INSTR]

    More complex resource names can be specified with the following grammar:
        GPIB[board]::primary address[::secondary address][::INSTR]

    Do not instantiate directly, use
    :meth:`pyvisa.highlevel.ResourceManager.open_resource`.

    """

    #: Whether to unaddress the device (UNT and UNL) after each read or write operation.
    enable_unaddressing: Attribute[bool] = attributes.AttrVI_ATTR_GPIB_UNADDR_EN()

    #: Whether to use repeat addressing before each read or write operation.
    enable_repeat_addressing: Attribute[bool] = attributes.AttrVI_ATTR_GPIB_READDR_EN()

    def wait_for_srq(self, timeout: int = 25000) -> None:
        """Wait for a serial request (SRQ) coming from the instrument.

        Note that this method is not ended when *another* instrument signals an
        SRQ, only *this* instrument.

        Parameters
        ----------
        timeout : int
            Maximum waiting time in milliseconds. Defaul: 25000 (milliseconds).
            None means waiting forever if necessary.

        """
        self.enable_event(
            constants.EventType.service_request, constants.EventMechanism.queue
        )

        if timeout and not (0 <= timeout <= 4294967295):
            raise ValueError("timeout value is invalid")

        starting_time = perf_counter()

        while True:
            if timeout is None:
                adjusted_timeout = constants.VI_TMO_INFINITE
            else:
                adjusted_timeout = int(
                    (starting_time + timeout / 1e3 - perf_counter()) * 1e3
                )
                if adjusted_timeout < 0:
                    adjusted_timeout = 0

            self.wait_on_event(constants.EventType.service_request, adjusted_timeout)
            if self.stb & 0x40:
                break

        self.discard_events(
            constants.EventType.service_request, constants.EventMechanism.queue
        )


@Resource.register(constants.InterfaceType.gpib, "INTFC")
class GPIBInterface(_GPIBMixin, MessageBasedResource):
    """Communicates with to devices of type GPIB::INTFC

    More complex resource names can be specified with the following grammar:
        GPIB[board]::INTFC

    Do not instantiate directly, use
    :meth:`pyvisa.highlevel.ResourceManager.open_resource`.

    """

    #: Is the specified GPIB interface currently the system controller.
    is_system_controller: Attribute[
        bool
    ] = attributes.AttrVI_ATTR_GPIB_SYS_CNTRL_STATE()

    #: Is the specified GPIB interface currently CIC (Controller In Charge).
    is_controller_in_charge: Attribute[bool] = attributes.AttrVI_ATTR_GPIB_CIC_STATE()

    #: Current state of the GPIB ATN (ATtentioN) interface line.
    atn_state: Attribute[constants.LineState] = attributes.AttrVI_ATTR_GPIB_ATN_STATE()

    #: Current state of the GPIB NDAC (Not Data ACcepted) interface line.
    ndac_state: Attribute[
        constants.LineState
    ] = attributes.AttrVI_ATTR_GPIB_NDAC_STATE()

    #: Is the GPIB interface currently addressed to talk or listen, or is not addressed.
    address_state: Attribute[
        constants.LineState
    ] = attributes.AttrVI_ATTR_GPIB_ADDR_STATE()

    def send_command(self, data: bytes) -> Tuple[int, constants.StatusCode]:
        """Write GPIB command bytes on the bus.

        Corresponds to viGpibCommand function of the VISA library.

        Parameters
        ----------
        data : bytes
            Command to write.

        Returns
        -------
        int
            Number of bytes written
        constants.StatusCode
            Return value of the library call.

        """
        return self.visalib.gpib_command(self.session, data)

    def control_atn(self, mode: constants.ATNLineOperation) -> constants.StatusCode:
        """Specifies the state of the ATN line and the local active controller state.

        Corresponds to viGpibControlATN function of the VISA library.

        Parameters
        ----------
        mode : constants.ATNLineOperation
            Specifies the state of the ATN line and optionally the local active
             controller state.

        Returns
        -------
        constants.StatusCode
            Return value of the library call.

        """
        return self.visalib.gpib_control_atn(self.session, mode)

    def pass_control(
        self, primary_address: int, secondary_address: int
    ) -> constants.StatusCode:
        """Tell a GPIB device to become controller in charge (CIC).

        Corresponds to viGpibPassControl function of the VISA library.

        Parameters
        ----------
        primary_address : int
            Primary address of the GPIB device to which you want to pass control.
        secondary_address : int
            Secondary address of the targeted GPIB device.
            If the targeted device does not have a secondary address,
            this parameter should contain the value Constants.NO_SEC_ADDR.

        Returns
        -------
        constants.StatusCode
            Return value of the library call.

        """
        return self.visalib.gpib_pass_control(
            self.session, primary_address, secondary_address
        )

    def send_ifc(self) -> constants.StatusCode:
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        Corresponds to viGpibSendIFC function of the VISA library.

        """
        return self.visalib.gpib_send_ifc(self.session)

    def group_execute_trigger(
        self, *resources: GPIBInstrument
    ) -> Tuple[int, constants.StatusCode]:
        """

        Parameters
        ----------
        resources : GPIBInstrument
            GPIB resources to which to send the group trigger.

        Returns
        -------
        int
            Number of bytes written as part of sending the GPIB commands.
        constants.StatusCode
            Return value of the library call.

        """
        for resource in resources:
            if not isinstance(resource, GPIBInstrument):
                raise ValueError("%r is not a GPIBInstrument", resource)

            # TODO: check that all resources are in the same board.

        if not self.is_controller_in_charge:
            self.send_ifc()

        command = [
            0x40,
            0x20 + 31,
        ]  # broadcast TAD#0 and "UNL" (don't listen) to all devices

        for resource in resources:
            # tell device GPIB::11 to listen
            command.append(0x20 + resource.primary_address)

        # send GET ('group execute trigger')
        command.append(0x08)

        return self.send_command(bytes(command))
