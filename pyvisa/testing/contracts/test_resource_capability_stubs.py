# -*- coding: utf-8 -*-
"""Capability-gated stubs for non-message and control-plane resource features."""

from __future__ import annotations

import time

import pytest

from pyvisa import constants
from pyvisa.constants import EventMechanism, EventType
from pyvisa.testing import CapabilityFlags, CommandMap
from pyvisa.testing.contracts._command_helpers import require_command
from pyvisa.testing.contracts._resource_matrix import (
    ALL_RESOURCE_SPECS,
    MESSAGE_BASED_RESOURCE_SPECS,
    ResourceSpec,
    contract_params,
)
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


def _resource_name_or_skip(profile, resource_key: str) -> str:
    resource_name = profile.resource_addresses.for_resource(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")
    return resource_name


def _capability_or_skip(capabilities: CapabilityFlags, resource_key: str) -> None:
    if not capabilities.transport_enabled_for_resource(resource_key, False):
        pytest.skip(
            f"Transport for {resource_key} is disabled for this backend/profile"
        )


def _resource_feature_or_skip(
    capabilities: CapabilityFlags,
    resource_key: str,
    feature_name: str,
) -> None:
    if not capabilities.resource_feature(resource_key, feature_name, False):
        pytest.skip(f"Feature {feature_name} is disabled for resource {resource_key}")


def _trigger_srq(instr, command_map: CommandMap) -> None:
    instr.write(require_command(command_map, "srq_payload"))
    instr.write(require_command(command_map, "srq_arm"))
    instr.write(require_command(command_map, "srq_trigger"))


def _message_resource_event_specs() -> tuple[ResourceSpec, ...]:
    return tuple(
        spec
        for spec in MESSAGE_BASED_RESOURCE_SPECS
        if spec.resource_key in {"TCPIP::INSTR", "TCPIP::HISLIP"}
    )


@pytest.mark.parametrize("resource_spec", contract_params(ALL_RESOURCE_SPECS))
def test_resource_locking_stub_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for resource-level lock/unlock lifecycle."""
    contract_id = f"resource.stub.locking.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, resource_spec.resource_key)
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        resource_spec.resource_key,
        "locking",
    )

    resource_name = _resource_name_or_skip(
        require_pyvisa_profile, resource_spec.resource_key
    )

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        instr.lock_excl()
        instr.unlock()
    finally:
        instr.close()


@pytest.mark.parametrize("resource_spec", contract_params(MESSAGE_BASED_RESOURCE_SPECS))
def test_resource_trigger_clear_stub_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for trigger and clear behavior on message-based resources."""
    contract_id = f"resource.stub.trigger_clear.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, resource_spec.resource_key)
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        resource_spec.resource_key,
        "trigger",
    )

    resource_name = _resource_name_or_skip(
        require_pyvisa_profile, resource_spec.resource_key
    )

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        instr.assert_trigger()
        instr.clear()
    finally:
        instr.close()


@pytest.mark.parametrize("resource_spec", contract_params(MESSAGE_BASED_RESOURCE_SPECS))
def test_resource_status_byte_stub_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for status-byte availability on message-based resources."""
    contract_id = f"resource.stub.status_byte.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, resource_spec.resource_key)
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        resource_spec.resource_key,
        "read_stb",
    )

    resource_name = _resource_name_or_skip(
        require_pyvisa_profile, resource_spec.resource_key
    )

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        status = instr.read_stb()
    finally:
        instr.close()

    assert isinstance(status, int)
    assert 0 <= status <= 0xFF


@pytest.mark.parametrize(
    "resource_spec", contract_params(_message_resource_event_specs())
)
def test_resource_srq_queue_stub_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    pyvisa_command_map: CommandMap,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for queue-based SRQ event signaling."""
    contract_id = f"resource.stub.event.queue.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, resource_spec.resource_key)
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        resource_spec.resource_key,
        "srq_queue",
    )

    resource_name = _resource_name_or_skip(
        require_pyvisa_profile, resource_spec.resource_key
    )

    instr = pyvisa_resource_manager.open_resource(resource_name)
    instr.timeout = 2000
    try:
        instr.clear()
        instr.enable_event(EventType.service_request, EventMechanism.queue, None)
        _trigger_srq(instr, pyvisa_command_map)
        try:
            response = instr.wait_on_event(EventType.service_request, 2000)
        finally:
            instr.disable_event(EventType.service_request, EventMechanism.queue)

        assert not response.timed_out
        assert response.event.event_type == EventType.service_request
    finally:
        instr.close()


@pytest.mark.parametrize(
    "resource_spec", contract_params(_message_resource_event_specs())
)
def test_resource_srq_handler_stub_contract(
    resource_spec: ResourceSpec,
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    pyvisa_command_map: CommandMap,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for handler-based SRQ event signaling."""
    contract_id = f"resource.stub.event.handler.{resource_spec.contract_suffix}"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, resource_spec.resource_key)
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        resource_spec.resource_key,
        "srq_handler",
    )

    resource_name = _resource_name_or_skip(
        require_pyvisa_profile, resource_spec.resource_key
    )

    class _Handler:
        def __init__(self) -> None:
            self.triggered = False

        def callback(self, session, event_type, event, handle=None):
            _ = (session, event, handle)
            if event_type == EventType.service_request:
                self.triggered = True
            return 0

    instr = pyvisa_resource_manager.open_resource(resource_name)
    instr.timeout = 2000
    try:
        handler = _Handler()
        user_handle = instr.install_handler(
            EventType.service_request,
            handler.callback,
            user_handle=1,
        )
        instr.enable_event(EventType.service_request, EventMechanism.handler, None)
        _trigger_srq(instr, pyvisa_command_map)
        try:
            t0 = time.time()
            while not handler.triggered and (time.time() - t0) < 2.5:
                time.sleep(0.1)
        finally:
            instr.disable_event(EventType.service_request, EventMechanism.handler)
            instr.uninstall_handler(
                EventType.service_request,
                handler.callback,
                user_handle,
            )

        assert handler.triggered
    finally:
        instr.close()


def test_usb_control_transfer_stub_contract(
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for USB control transfer support."""
    contract_id = "resource.stub.usb.control_transfer.usb::instr"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, "usb")
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        "USB::INSTR",
        "control_transfer",
    )

    resource_name = _resource_name_or_skip(require_pyvisa_profile, "USB::INSTR")

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        result = instr.control_in(0xC0, 0x01, 0, 0, 1)
        assert isinstance(result, (bytes, bytearray))
        status = instr.control_out(0x40, 0x01, 0, 0, b"\x00")
        assert status is None or isinstance(status, int)
    finally:
        instr.close()


def test_usb_attributes_stub_contract(
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for USB INSTR attribute visibility and typing."""
    contract_id = "resource.stub.usb.attributes.usb::instr"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, "usb")
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        "USB::INSTR",
        "attributes",
    )

    resource_name = _resource_name_or_skip(require_pyvisa_profile, "USB::INSTR")

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        interface_number = instr.get_visa_attribute(
            constants.ResourceAttribute.usb_interface_number
        )
        serial_number = instr.get_visa_attribute(
            constants.ResourceAttribute.usb_serial_number
        )
        manufacturer_name = instr.get_visa_attribute(
            constants.ResourceAttribute.manufacturer_name
        )
        model_name = instr.get_visa_attribute(constants.ResourceAttribute.model_name)
    finally:
        instr.close()

    assert isinstance(interface_number, int)
    assert interface_number >= 0
    assert isinstance(serial_number, str)
    assert serial_number
    assert isinstance(manufacturer_name, str)
    assert isinstance(model_name, str)


def test_gpib_intfc_bus_control_stub_contract(
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for GPIB interface controller operations."""
    contract_id = "resource.stub.gpib.intfc.bus_control"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, "gpib")
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        "GPIB::INTFC",
        "bus_control",
    )

    resource_name = _resource_name_or_skip(require_pyvisa_profile, "GPIB::INTFC")

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        instr.send_ifc()
        for method_name in ("control_atn", "send_command", "pass_control"):
            assert hasattr(instr, method_name)
    finally:
        instr.close()


def test_gpib_intfc_controller_ops_stub_contract(
    require_pyvisa_profile,
    pyvisa_backend_capabilities: CapabilityFlags,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Stub contract for GPIB INTFC controller operations."""
    contract_id = "resource.stub.gpib.intfc.controller_ops"
    apply_pyvisa_contract_policy(contract_id)

    _capability_or_skip(pyvisa_backend_capabilities, "gpib")
    _resource_feature_or_skip(
        pyvisa_backend_capabilities,
        "GPIB::INTFC",
        "controller_ops",
    )

    resource_name = _resource_name_or_skip(require_pyvisa_profile, "GPIB::INTFC")

    instr = pyvisa_resource_manager.open_resource(resource_name)
    try:
        atn_status = instr.control_atn(constants.ATNLineOperation.asrt)
        sent_count, send_status = instr.send_command(
            bytes([constants.GPIBCommand.unlisten])
        )
        pass_status = instr.pass_control(1, constants.NO_SEC_ADDR)
    finally:
        instr.close()

    assert isinstance(atn_status, constants.StatusCode)
    assert sent_count >= 1
    assert isinstance(send_status, constants.StatusCode)
    assert isinstance(pass_status, constants.StatusCode)
