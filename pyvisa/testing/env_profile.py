# -*- coding: utf-8 -*-
"""Environment-based instrument profile loading for shared contract tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from .profiles import (
    CapabilityFlags,
    CommandMap,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
)


def discover_env_file() -> Path | None:
    """Find an env file path for PYVISA_TESTER_* test configuration."""
    explicit = os.environ.get("PYVISA_TESTER_ENV_FILE")
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.is_file() else None

    for candidate in (Path("pyvisa_tester.env"), Path(".pyvisa_tester.env")):
        if candidate.is_file():
            return candidate

    return None


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse KEY=VALUE lines from a dotenv-like file."""
    values: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip()
    return values


def load_tester_env_from_file() -> Dict[str, str]:
    """Load PYVISA_TESTER_* variables from a discovered env file."""
    path = discover_env_file()
    if path is None:
        return {}

    loaded = parse_env_file(path)
    for key, value in loaded.items():
        if key.startswith("PYVISA_TESTER_"):
            os.environ.setdefault(key, value)

    os.environ.setdefault("PYVISA_TESTER_ENV_FILE", str(path.resolve()))
    return loaded


def profile_from_environment() -> InstrumentProfile | None:
    """Build an instrument profile from PYVISA_TESTER_* environment values."""
    load_tester_env_from_file()

    if os.environ.get("PYVISA_TESTER_ASSISTED") != "1":
        return None

    resource_addresses = ResourceAddresses(
        tcpip_instr=os.environ.get(
            "PYVISA_TESTER_VXI11_ADDR", "TCPIP::127.0.0.1::inst0::INSTR"
        ),
        tcpip_hislip=os.environ.get(
            "PYVISA_TESTER_HISLIP_ADDR", "TCPIP::127.0.0.1::hislip0::INSTR"
        ),
        tcpip_socket=os.environ.get(
            "PYVISA_TESTER_SOCKET_ADDR", "TCPIP::127.0.0.1::5025::SOCKET"
        ),
        usb_instr=os.environ.get(
            "PYVISA_TESTER_USB_INSTR_ADDR", "USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR"
        ),
        gpib_instr=os.environ.get("PYVISA_TESTER_GPIB_INSTR_ADDR", "GPIB0::1::INSTR"),
        gpib_intfc=os.environ.get("PYVISA_TESTER_GPIB_INTFC_ADDR", "GPIB0::INTFC"),
        asrl_instr=os.environ.get("PYVISA_TESTER_ASRL_INSTR_ADDR", "ASRL1::INSTR"),
    )

    capabilities = CapabilityFlags(
        transport_vxi11=os.environ.get("PYVISA_TESTER_VXI11", "1") != "0",
        transport_hislip=os.environ.get("PYVISA_TESTER_HISLIP", "1") != "0",
        transport_socket=os.environ.get("PYVISA_TESTER_SOCKET", "1") != "0",
        transport_usb=os.environ.get("PYVISA_TESTER_USB", "1") != "0",
        transport_gpib=os.environ.get("PYVISA_TESTER_GPIB", "0") != "0",
        transport_asrl=os.environ.get("PYVISA_TESTER_ASRL", "0") != "0",
        resource_gpib_intfc_query=os.environ.get("PYVISA_TESTER_GPIB_INTFC_QUERY", "0")
        != "0",
    )

    command_map = CommandMap(
        identity_query=os.environ.get("PYVISA_TESTER_CMD_IDENTITY_QUERY", "*IDN?"),
        shared_query=os.environ.get("PYVISA_TESTER_CMD_SHARED_QUERY", "QUERY?"),
        health_query=os.environ.get("PYVISA_TESTER_CMD_HEALTH_QUERY", "SYST:HEALTH?"),
        error_query=os.environ.get("PYVISA_TESTER_CMD_ERROR_QUERY", "SYST:ERR?"),
        binary_query_template=os.environ.get(
            "PYVISA_TESTER_CMD_BINARY_QUERY_TEMPLATE",
            "DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        ),
        binary_configure_template=os.environ.get(
            "PYVISA_TESTER_CMD_BINARY_CONFIGURE_TEMPLATE",
            "DATA:BIN:CFG {datatype},{count},{endian},{header},{termination},{pattern},{start}",
        ),
        binary_read_query=os.environ.get(
            "PYVISA_TESTER_CMD_BINARY_READ_QUERY", "DATA:BIN:READ?"
        ),
        srq_payload=os.environ.get("PYVISA_TESTER_CMD_SRQ_PAYLOAD", "DATA:PAYLOAD 1"),
        srq_expected_read=os.environ.get("PYVISA_TESTER_CMD_SRQ_EXPECTED_READ", "1"),
        srq_arm=os.environ.get("PYVISA_TESTER_CMD_SRQ_ARM", "EVEN:SRQ:ARM 1"),
        srq_trigger=os.environ.get("PYVISA_TESTER_CMD_SRQ_TRIGGER", "EVEN:SRQ:TRIG"),
        srq_clear=os.environ.get("PYVISA_TESTER_CMD_SRQ_CLEAR", "EVEN:SRQ:CLE"),
    )

    return InstrumentProfile(
        name=os.environ.get("PYVISA_TESTER_PROFILE", "pyvisa-tester-env"),
        resource_addresses=resource_addresses,
        expected_idn=os.environ.get(
            "PYVISA_TESTER_EXPECTED_IDN",
            "Cyberdyne systems,T800 Model 101,A9012.C,V2.4",
        ),
        command_map=command_map,
        capabilities=capabilities,
        metadata=ProfileMetadata(source="env", target="pyvisa-tester"),
    )
