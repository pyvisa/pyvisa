# -*- coding: utf-8 -*-
"""Shared resource-class capability matrix for backend contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSpec:
    """Contract metadata for one logical resource class."""

    resource_key: str
    transport_capability_attr: str
    expected_class: str
    message_based: bool = True
    query_capability_attr: str | None = None
    default_query_enabled: bool = True

    @property
    def contract_suffix(self) -> str:
        return self.resource_key.lower()


ALL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        "TCPIP::INSTR",
        "transport_vxi11",
        "INSTR",
        query_capability_attr="resource_query_tcpip_instr",
    ),
    ResourceSpec(
        "TCPIP::HISLIP",
        "transport_hislip",
        "INSTR",
        query_capability_attr="resource_query_tcpip_hislip",
    ),
    ResourceSpec(
        "TCPIP::SOCKET",
        "transport_socket",
        "SOCKET",
        query_capability_attr="resource_query_tcpip_socket",
    ),
    ResourceSpec(
        "USB::INSTR",
        "transport_usb",
        "INSTR",
        query_capability_attr="resource_query_usb_instr",
    ),
    ResourceSpec(
        "GPIB::INSTR",
        "transport_gpib",
        "INSTR",
        query_capability_attr="resource_query_gpib_instr",
    ),
    ResourceSpec(
        "GPIB::INTFC",
        "transport_gpib",
        "INTFC",
        message_based=False,
        query_capability_attr="resource_gpib_intfc_query",
        default_query_enabled=False,
    ),
    ResourceSpec(
        "ASRL::INSTR",
        "transport_asrl",
        "INSTR",
        query_capability_attr="resource_query_asrl_instr",
    ),
)

MESSAGE_BASED_RESOURCE_SPECS: tuple[ResourceSpec, ...] = tuple(
    spec for spec in ALL_RESOURCE_SPECS if spec.message_based
)


def contract_params(specs: tuple[ResourceSpec, ...]) -> list:
    """Build stable pytest params with readable ids from resource specs."""
    import pytest

    return [pytest.param(spec, id=spec.contract_suffix) for spec in specs]
