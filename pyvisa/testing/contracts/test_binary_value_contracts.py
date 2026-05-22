# -*- coding: utf-8 -*-
"""Shared binary transfer contracts for backend implementations."""

from __future__ import annotations

import pytest

from pyvisa.testing.requirements import require_visa_lib

pytestmark = [
    require_visa_lib,
    pytest.mark.pyvisa_contract,
    pytest.mark.pyvisa_hardware,
]


@pytest.mark.parametrize(
    "resource_key, capability_key",
    [
        ("TCPIP::INSTR", "transport.vxi11"),
        ("TCPIP::HISLIP", "transport.hislip"),
    ],
)
@pytest.mark.parametrize(
    "header_fmt, is_big_endian, header_token, termination_token, expect_termination, contract_suffix",
    [
        ("ieee", False, "ieee", "none", False, "ieee"),
        ("hp", True, "hp", "none", False, "hp"),
        ("empty", False, "empty", "lf", True, "empty_lf"),
    ],
)
def test_binary_query_u16_ramp_contract(
    resource_key: str,
    capability_key: str,
    header_fmt: str,
    is_big_endian: bool,
    header_token: str,
    termination_token: str,
    expect_termination: bool,
    contract_suffix: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_command_map,
    apply_pyvisa_contract_policy,
):
    """Validate binary query parsing for u16 ramp payloads across TCPIP transports."""
    contract_id = f"binary.query.{contract_suffix}.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not pyvisa_backend_capabilities.get(capability_key, True):
        pytest.skip(f"Capability {capability_key} is disabled for this backend/profile")

    resource_name = require_pyvisa_profile.resource_addresses.get(resource_key)
    if not resource_name:
        pytest.skip(f"Profile does not define resource address for {resource_key}")

    health_query = pyvisa_command_map.get("health_query", "SYST:HEALTH?")
    query_template = pyvisa_command_map.get(
        "binary_query_template",
        "DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    )
    query = query_template.format(
        datatype="u16",
        count=4,
        endian="be" if is_big_endian else "le",
        header=header_token,
        termination=termination_token,
        pattern="ramp",
        start=1,
    )

    from pyvisa import ResourceManager

    rm = ResourceManager()
    try:
        instr = rm.open_resource(resource_name)
        instr.timeout = 2000
        instr.read_termination = ""
        instr.write_termination = "\n"
        try:
            # Health probing is optional across instruments; if available we use
            # it only as an early capability hint.
            try:
                health = instr.query(health_query).strip().lower()
            except Exception:
                health = ""

            if health and "data=asc,bin" not in health:
                pytest.skip("Instrument health check reports no binary query support")

            kwargs = {
                "datatype": "H",
                "is_big_endian": is_big_endian,
                "header_fmt": header_fmt,
                "expect_termination": expect_termination,
            }
            if header_fmt == "empty":
                kwargs["data_points"] = 4

            values = instr.query_binary_values(query, **kwargs)
        finally:
            instr.close()
    finally:
        rm.close()

    assert values == [0, 1, 2, 3]
