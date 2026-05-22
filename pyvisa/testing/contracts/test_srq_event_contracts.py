# -*- coding: utf-8 -*-
"""Shared SRQ event contracts for backend implementations."""

from __future__ import annotations

import time

import pytest

from pyvisa.constants import EventMechanism, EventType
from pyvisa.testing.contracts._event_helpers import compare_user_handle
from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


class _EventHandler:
    def __init__(self) -> None:
        self.event_success = False
        self.srq_success = False
        self.handle = None
        self.session = None

    def handle_event(self, session, event_type, event, handle=None):
        self.session = session
        self.handle = handle
        if event_type == EventType.service_request:
            self.event_success = True
            self.srq_success = True
        return 0


def _trigger_srq(instr, command_map: dict[str, str]) -> None:
    instr.write(command_map.get("srq_payload", "DATA:PAYLOAD 1"))
    instr.write(command_map.get("srq_arm", "EVEN:SRQ:ARM 1"))
    instr.write(command_map.get("srq_trigger", "EVEN:SRQ:TRIG"))


@pytest.mark.parametrize(
    "resource_key, capability_key",
    [
        ("TCPIP::INSTR", "transport.vxi11"),
        ("TCPIP::HISLIP", "transport.hislip"),
    ],
)
def test_srq_queue_event_contract(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_command_map,
    apply_pyvisa_contract_policy,
):
    """Validate queue-based SRQ handling across supported TCPIP transports."""
    contract_id = f"srq.queue.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    if not pyvisa_backend_capabilities.get("events.srq", True):
        pytest.skip("Capability events.srq is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    instr = rm.open_resource(resource_name)
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
        assert instr.read() == pyvisa_command_map.get("srq_expected_read", "1")
    finally:
        instr.close()
        rm.close()


@pytest.mark.parametrize(
    "resource_key, capability_key",
    [
        ("TCPIP::INSTR", "transport.vxi11"),
        ("TCPIP::HISLIP", "transport.hislip"),
    ],
)
def test_srq_handler_event_contract(
    resource_key: str,
    capability_key: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_command_map,
    apply_pyvisa_contract_policy,
):
    """Validate handler-based SRQ handling across supported TCPIP transports."""
    contract_id = f"srq.handler.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    if not pyvisa_backend_capabilities.get("events.srq", True):
        pytest.skip("Capability events.srq is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    from pyvisa import ResourceManager

    rm = ResourceManager()
    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    try:
        handler = _EventHandler()
        user_handle = instr.install_handler(
            EventType.service_request, handler.handle_event, user_handle=1
        )
        instr.enable_event(EventType.service_request, EventMechanism.handler, None)
        _trigger_srq(instr, pyvisa_command_map)

        try:
            t0 = time.time()
            while not handler.event_success and (time.time() - t0) < 2.5:
                time.sleep(0.1)
        finally:
            instr.disable_event(EventType.service_request, EventMechanism.handler)
            instr.uninstall_handler(
                EventType.service_request, handler.handle_event, user_handle
            )

        assert handler.session == instr.session
        assert compare_user_handle(handler.handle, user_handle)
        assert handler.srq_success
        assert instr.read() == pyvisa_command_map.get("srq_expected_read", "1")
    finally:
        instr.close()
        rm.close()
