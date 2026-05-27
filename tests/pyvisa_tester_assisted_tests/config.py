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
    {
        "TCPIP::INSTR": "TCPIP::127.0.0.1::inst0::INSTR",
        "TCPIP::HISLIP": "TCPIP::127.0.0.1::hislip0::INSTR",
        "TCPIP::SOCKET": "TCPIP::127.0.0.1::5025::SOCKET",
        "USB::INSTR": "USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR",
    }
)

PYVISA_TESTER_EXPECTED_IDN = "Cyberdyne systems,T800 Model 101,A9012.C,V2.4"

PYVISA_TESTER_COMMAND_MAP = CommandMap(
    {
        "identity_query": "*IDN?",
        "shared_query": "QUERY?",
        "health_query": "SYST:HEALTH?",
        "error_query": "SYST:ERR?",
        "binary_query_template": "DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        "binary_configure_template": "DATA:BIN:CFG {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        "binary_read_query": "DATA:BIN:READ?",
        "srq_arm": "EVEN:SRQ:ARM 1",
        "srq_trigger": "EVEN:SRQ:TRIG",
        "srq_clear": "EVEN:SRQ:CLE",
    }
)

PYVISA_TESTER_CAPABILITIES = CapabilityFlags(
    {
        "transport.vxi11": True,
        "transport.hislip": True,
        "transport.socket": True,
        "transport.usb": True,
        "transport.gpib": False,
        "transport.asrl": False,
        "events.srq": True,
        "locking.shared": True,
        "resource.gpib.intfc.query": False,
        "resource.locking.tcpip.instr": True,
        "resource.locking.tcpip.hislip": True,
        "resource.locking.tcpip.socket": False,
        "resource.trigger.tcpip.instr": True,
        "resource.trigger.tcpip.hislip": True,
        "resource.trigger.tcpip.socket": False,
        "resource.read_stb.tcpip.instr": True,
        "resource.read_stb.tcpip.hislip": True,
        "resource.read_stb.tcpip.socket": False,
        "resource.event.srq.queue.tcpip.instr": True,
        "resource.event.srq.queue.tcpip.hislip": True,
        "resource.event.srq.handler.tcpip.instr": True,
        "resource.event.srq.handler.tcpip.hislip": True,
        "resource.usb.control_transfer": False,
        "resource.usb.attributes": False,
        "resource.gpib.intfc.controller_ops": False,
    }
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
