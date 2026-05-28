# -*- coding: utf-8 -*-
"""In-code pyvisa-tester assisted test configuration."""

from __future__ import annotations

from pyvisa.testing import (
    CapabilityFlags,
    CommandMap,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
)

PYVISA_TESTER_RESOURCE_ADDRESSES = ResourceAddresses(
    tcpip_instr="TCPIP::127.0.0.1::inst0::INSTR",
    tcpip_hislip="TCPIP::127.0.0.1::hislip0::INSTR",
    tcpip_socket="TCPIP::127.0.0.1::5025::SOCKET",
    usb_instr="USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR",
)

PYVISA_TESTER_EXPECTED_IDN = "Cyberdyne systems,T800 Model 101,A9012.C,V2.4"

PYVISA_TESTER_COMMAND_MAP = CommandMap(
    identity_query="*IDN?",
    shared_query="QUERY?",
    health_query="SYST:HEALTH?",
    error_query="SYST:ERR?",
    binary_query_template="DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    binary_configure_template="DATA:BIN:CFG {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    binary_read_query="DATA:BIN:READ?",
    srq_payload="DATA:PAYLOAD 1",
    srq_expected_read="1",
    srq_arm="EVEN:SRQ:ARM 1",
    srq_trigger="EVEN:SRQ:TRIG",
    srq_clear="EVEN:SRQ:CLE",
)

PYVISA_TESTER_CAPABILITIES = CapabilityFlags(
    transport_vxi11=True,
    transport_hislip=True,
    transport_socket=True,
    transport_usb=True,
    transport_gpib=False,
    transport_asrl=False,
    events_srq=True,
    locking_shared=True,
    resource_gpib_intfc_query=False,
    resource_locking_tcpip_instr=True,
    resource_locking_tcpip_hislip=True,
    resource_locking_tcpip_socket=False,
    resource_trigger_tcpip_instr=True,
    resource_trigger_tcpip_hislip=True,
    resource_trigger_tcpip_socket=False,
    resource_read_stb_tcpip_instr=True,
    resource_read_stb_tcpip_hislip=True,
    resource_read_stb_tcpip_socket=False,
    resource_event_srq_queue_tcpip_instr=True,
    resource_event_srq_queue_tcpip_hislip=True,
    resource_event_srq_handler_tcpip_instr=True,
    resource_event_srq_handler_tcpip_hislip=True,
    resource_usb_control_transfer=False,
    resource_usb_attributes=False,
    resource_gpib_intfc_controller_ops=False,
)


def build_pyvisa_tester_profile() -> InstrumentProfile:
    """Build the default in-code pyvisa-tester profile for pyvisa tests."""
    return InstrumentProfile(
        name="pyvisa-tester-code",
        resource_addresses=PYVISA_TESTER_RESOURCE_ADDRESSES,
        expected_idn=PYVISA_TESTER_EXPECTED_IDN,
        command_map=PYVISA_TESTER_COMMAND_MAP,
        capabilities=PYVISA_TESTER_CAPABILITIES,
        metadata=ProfileMetadata(source="pyvisa-tests", target="pyvisa-tester"),
    )
