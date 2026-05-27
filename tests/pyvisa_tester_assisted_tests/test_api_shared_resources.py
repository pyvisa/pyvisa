# -*- coding: utf-8 -*-
"""Transport-shared API-level assisted tests.

These tests intentionally use only pyvisa public API and run across transports
where capabilities overlap.
"""

from __future__ import annotations

import pytest

from pyvisa.testing.requirements import require_visa_lib

from . import EXPECTED_IDN

pytestmark = [
    require_visa_lib,
    pytest.mark.usefixtures("require_pyvisa_tester_profile"),
    pytest.mark.pyvisa_tester_assisted,
    pytest.mark.pyvisa_tester_shared,
]


def _open_resource_for_transport(resource_key: str, resource_name: str):
    from pyvisa import ResourceManager

    rm = ResourceManager()
    instr = rm.open_resource(resource_name)
    instr.timeout = 2000
    if resource_key == "TCPIP::SOCKET":
        instr.read_termination = "\n"
        instr.write_termination = "\n"
    else:
        instr.read_termination = ""
        instr.write_termination = "\n"
    return rm, instr


@pytest.mark.parametrize(
    "resource_key",
    [
        "TCPIP::INSTR",
        "TCPIP::HISLIP",
        "TCPIP::SOCKET",
    ],
)
def test_shared_idn_and_query(
    resource_key,
    require_assisted_resource,
    require_assisted_command,
    require_pyvisa_profile,
):
    resource_name = require_assisted_resource(resource_key)
    idn_query = require_assisted_command("identity_query")
    shared_query = require_assisted_command("shared_query")
    rm, instr = _open_resource_for_transport(resource_key, resource_name)
    try:
        expected_idn = require_pyvisa_profile.expected_idn or EXPECTED_IDN
        assert instr.query(idn_query).strip() == expected_idn
        assert instr.query(shared_query).strip() == "RESPONSE"
    finally:
        instr.close()
        rm.close()


@pytest.mark.parametrize(
    "resource_key",
    [
        "TCPIP::INSTR",
        "TCPIP::HISLIP",
    ],
)
def test_shared_binary_query(
    resource_key, require_assisted_resource, require_assisted_command
):
    resource_name = require_assisted_resource(resource_key)
    binary_query = require_assisted_command("binary_query_template").format(
        datatype="u16",
        count=4,
        endian="le",
        header="ieee",
        termination="none",
        pattern="ramp",
        start=1,
    )
    rm, instr = _open_resource_for_transport(resource_key, resource_name)
    try:
        values = instr.query_binary_values(
            binary_query,
            datatype="H",
            is_big_endian=False,
            header_fmt="ieee",
            expect_termination=False,
        )
        assert values == [0, 1, 2, 3]
    finally:
        instr.close()
        rm.close()
