# -*- coding: utf-8 -*-
"""Data models used by shared backend contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class InstrumentProfile:
    """Resolved target used to run contract tests.

    Attributes
    ----------
    name:
        Human-friendly profile name.
    resource_addresses:
        Mapping from abstract resource kinds to VISA resource strings.
        Typical keys: TCPIP::INSTR, TCPIP::HISLIP, TCPIP::SOCKET, USB::INSTR.
    expected_idn:
        Optional value expected by identity tests.
    command_map:
        Semantic command identifiers mapped to concrete instrument commands.
    capabilities:
        Capability flags used by tests to decide which checks to execute.
    metadata:
        Optional additional context attached by profile providers.
    """

    name: str
    resource_addresses: Mapping[str, str] = field(default_factory=dict)
    expected_idn: str | None = None
    command_map: Mapping[str, str] = field(default_factory=dict)
    capabilities: Mapping[str, bool] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
