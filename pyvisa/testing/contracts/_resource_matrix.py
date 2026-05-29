# -*- coding: utf-8 -*-
"""Shared resource-class capability matrix for backend contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSpec:
    """Contract metadata for one logical resource class."""

    resource_key: str
    transport_key: str
    resource_class: str
    expected_class: str
    message_based: bool = True
    default_query_enabled: bool = True

    @property
    def contract_suffix(self) -> str:
        return self.resource_key.lower()


ALL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        "TCPIP::INSTR",
        "vxi11",
        "INSTR",
        "INSTR",
    ),
    ResourceSpec(
        "TCPIP::HISLIP",
        "hislip",
        "INSTR",
        "INSTR",
    ),
    ResourceSpec(
        "TCPIP::SOCKET",
        "socket",
        "SOCKET",
        "SOCKET",
    ),
    ResourceSpec(
        "USB::INSTR",
        "usb",
        "INSTR",
        "INSTR",
    ),
    ResourceSpec(
        "GPIB::INSTR",
        "gpib",
        "INSTR",
        "INSTR",
    ),
    ResourceSpec(
        "GPIB::INTFC",
        "gpib",
        "INTFC",
        "INTFC",
        message_based=False,
        default_query_enabled=False,
    ),
    ResourceSpec(
        "ASRL::INSTR",
        "asrl",
        "INSTR",
        "INSTR",
    ),
)

MESSAGE_BASED_RESOURCE_SPECS: tuple[ResourceSpec, ...] = tuple(
    spec for spec in ALL_RESOURCE_SPECS if spec.message_based
)


def contract_params(specs: tuple[ResourceSpec, ...]) -> list:
    """Build stable pytest params with readable ids from resource specs."""
    import pytest

    return [pytest.param(spec, id=spec.contract_suffix) for spec in specs]
