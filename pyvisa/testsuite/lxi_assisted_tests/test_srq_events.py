# -*- coding: utf-8 -*-
"""SRQ event tests for LXI-assisted TCPIP INSTR resources.

These tests validate that service request events can be observed through both
queue and handler mechanisms.
"""

import ctypes
import time

import pytest

from pyvisa import ResourceManager
from pyvisa.constants import EventMechanism, EventType
from pyvisa.testsuite import require_visa_lib

from . import (
    RESOURCE_ADDRESSES,
    require_lxi_assisted,
    require_lxi_hislip,
    require_lxi_vxi11,
)

pytestmark = [require_visa_lib, require_lxi_assisted]


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


def _compare_user_handle(h1, h2):
    if isinstance(h1, ctypes.Structure):
        return h1 == h2
    if hasattr(h1, "value"):
        return h1.value == h2.value
    if isinstance(h1, (tuple, list)):
        return all((i == j for i, j in zip(h1, h2)))
    return h1 == h2


def _trigger_srq(instr):
    instr.write("DATA:PAYLOAD 1")
    instr.write("EVEN:SRQ:ARM 1")
    instr.write("EVEN:SRQ:TRIG")


def _run_queue_srq_flow(resource_name: str):
    rm = ResourceManager()
    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    try:
        instr.clear()
        instr.enable_event(EventType.service_request, EventMechanism.queue, None)
        _trigger_srq(instr)
        try:
            response = instr.wait_on_event(EventType.service_request, 2000)
        finally:
            instr.disable_event(EventType.service_request, EventMechanism.queue)

        assert not response.timed_out
        assert response.event.event_type == EventType.service_request
        assert instr.read() == "1"
    finally:
        instr.close()
        rm.close()


def _run_handler_srq_flow(resource_name: str):
    rm = ResourceManager()
    if "hislip" in resource_name.lower() and rm.visalib.library_path == "py":
        pytest.skip("pyvisa-py does not support HiSLIP")

    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    try:
        handler = _EventHandler()
        user_handle = instr.install_handler(
            EventType.service_request, handler.handle_event, user_handle=1
        )
        instr.enable_event(EventType.service_request, EventMechanism.handler, None)
        _trigger_srq(instr)

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
        assert _compare_user_handle(handler.handle, user_handle)
        assert handler.srq_success
        assert instr.read() == "1"
    finally:
        instr.close()
        rm.close()


@require_lxi_vxi11
def test_vxi11_srq_queue_event():
    _run_queue_srq_flow(RESOURCE_ADDRESSES["TCPIP::INSTR"])


@require_lxi_vxi11
def test_vxi11_srq_handler_event():
    _run_handler_srq_flow(RESOURCE_ADDRESSES["TCPIP::INSTR"])


@require_lxi_hislip
def test_hislip_srq_queue_event():
    _run_queue_srq_flow(RESOURCE_ADDRESSES["TCPIP::HISLIP"])


@require_lxi_hislip
def test_hislip_srq_handler_event():
    _run_handler_srq_flow(RESOURCE_ADDRESSES["TCPIP::HISLIP"])
