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


def _capability_or_default(capabilities, attr_name: str, default: bool) -> bool:
    value = getattr(capabilities, attr_name)
    return default if value is None else bool(value)


def _binary_query_kwargs(
    header_fmt: str,
    is_big_endian: bool,
    expect_termination: bool,
) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "datatype": "H",
        "is_big_endian": is_big_endian,
        "header_fmt": header_fmt,
        "expect_termination": expect_termination,
    }
    if header_fmt == "empty":
        kwargs["data_points"] = 4
    return kwargs


@pytest.mark.parametrize(
    "resource_key, capability_attr",
    [
        ("TCPIP::INSTR", "transport_vxi11"),
        ("TCPIP::HISLIP", "transport_hislip"),
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
    capability_attr: str,
    header_fmt: str,
    is_big_endian: bool,
    header_token: str,
    termination_token: str,
    expect_termination: bool,
    contract_suffix: str,
    require_pyvisa_profile,
    pyvisa_backend_capabilities,
    pyvisa_instrument_pool,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Validate binary query parsing for u16 ramp payloads across TCPIP transports."""
    contract_id = f"binary.query.{contract_suffix}.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not _capability_or_default(pyvisa_backend_capabilities, capability_attr, True):
        pytest.skip(
            f"Capability {capability_attr} is disabled for this backend/profile"
        )

    if not pyvisa_instrument_pool.supports_resource(resource_key):
        pytest.skip(f"Instrument pool does not define resource {resource_key}")

    resource = pyvisa_instrument_pool.for_resource(resource_key)
    query = resource.binary_query(
        datatype="u16",
        count=4,
        endian="be" if is_big_endian else "le",
        header=header_token,
        termination=termination_token,
        pattern="ramp",
        start=1,
    )

    rm = pyvisa_resource_manager
    instr = rm.open_resource(resource.resource_name)
    instr.timeout = 2000
    instr.read_termination = ""
    instr.write_termination = "\n"
    try:
        resource.prepare_binary_query(instr)
        values = instr.query_binary_values(
            query,
            **_binary_query_kwargs(
                header_fmt,
                is_big_endian,
                expect_termination,
            ),
        )
    finally:
        instr.close()

    assert values == [0, 1, 2, 3]


@pytest.mark.parametrize(
    "resource_key, capability_attr",
    [
        ("TCPIP::INSTR", "transport_vxi11"),
        ("TCPIP::HISLIP", "transport_hislip"),
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
def test_binary_staged_transfer_contract(
    resource_key: str,
    capability_attr: str,
    header_fmt: str,
    is_big_endian: bool,
    header_token: str,
    termination_token: str,
    expect_termination: bool,
    contract_suffix: str,
    pyvisa_backend_capabilities,
    pyvisa_instrument_pool,
    apply_pyvisa_contract_policy,
    pyvisa_resource_manager,
):
    """Validate staged binary transfers via error-state checks and optional readback."""
    contract_id = f"binary.staged.{contract_suffix}.{resource_key.lower()}"
    apply_pyvisa_contract_policy(contract_id)

    if not _capability_or_default(pyvisa_backend_capabilities, capability_attr, True):
        pytest.skip(
            f"Capability {capability_attr} is disabled for this backend/profile"
        )

    if not pyvisa_instrument_pool.supports_resource(resource_key):
        pytest.skip(f"Instrument pool does not define resource {resource_key}")

    resource = pyvisa_instrument_pool.for_resource(resource_key)
    try:
        config_command = resource.binary_configure(
            datatype="u16",
            count=4,
            endian="be" if is_big_endian else "le",
            header=header_token,
            termination=termination_token,
            pattern="ramp",
            start=1,
        )
    except NotImplementedError as exc:
        pytest.skip(str(exc))

    try:
        readback_query = resource.binary_read_query()
    except NotImplementedError:
        readback_query = None

    error_checked = False
    readback_checked = False
    rm = pyvisa_resource_manager
    instr = rm.open_resource(resource.resource_name)
    instr.timeout = 2000
    instr.read_termination = ""
    instr.write_termination = "\n"
    try:
        resource.prepare_binary_query(instr)
        instr.write(config_command)

        try:
            resource.verify_no_instrument_error(instr)
        except NotImplementedError:
            pass
        else:
            error_checked = True

        if readback_query is not None:
            values = instr.query_binary_values(
                readback_query,
                **_binary_query_kwargs(
                    header_fmt,
                    is_big_endian,
                    expect_termination,
                ),
            )
            assert values == [0, 1, 2, 3]
            readback_checked = True
    finally:
        instr.close()

    assert error_checked or readback_checked, (
        "Instrument pool exposes neither error-state nor readback validation"
    )
