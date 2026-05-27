# -*- coding: utf-8 -*-
"""Shared resource-class capability matrix for backend contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSpec:
    """Contract metadata for one logical resource class."""

    resource_key: str
    capability_key: str
    expected_class: str
    message_based: bool = True
    query_capability_key: str | None = None
    default_query_enabled: bool = True

    @property
    def contract_suffix(self) -> str:
        return self.resource_key.lower()


ALL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec("TCPIP::INSTR", "transport.vxi11", "INSTR"),
    ResourceSpec("TCPIP::HISLIP", "transport.hislip", "INSTR"),
    ResourceSpec("TCPIP::SOCKET", "transport.socket", "SOCKET"),
    ResourceSpec("USB::INSTR", "transport.usb", "INSTR"),
    ResourceSpec("GPIB::INSTR", "transport.gpib", "INSTR"),
    ResourceSpec(
        "GPIB::INTFC",
        "transport.gpib",
        "INTFC",
        message_based=False,
        query_capability_key="resource.gpib.intfc.query",
        default_query_enabled=False,
    ),
    ResourceSpec("ASRL::INSTR", "transport.asrl", "INSTR"),
)

MESSAGE_BASED_RESOURCE_SPECS: tuple[ResourceSpec, ...] = tuple(
    spec for spec in ALL_RESOURCE_SPECS if spec.message_based
)


def contract_params(specs: tuple[ResourceSpec, ...]) -> list:
    """Build stable pytest params with readable ids from resource specs."""
    import pytest

    return [pytest.param(spec, id=spec.contract_suffix) for spec in specs]
