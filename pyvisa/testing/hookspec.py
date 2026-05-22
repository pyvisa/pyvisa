# -*- coding: utf-8 -*-
"""Pytest hook specifications for PyVISA shared backend contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest
from pluggy import HookspecMarker

from .profiles import InstrumentProfile

hookspec = HookspecMarker("pytest")


@hookspec(firstresult=True)
def pytest_pyvisa_select_profile(
    config: pytest.Config, profile_name: str
) -> InstrumentProfile | None:
    """Return the selected instrument profile, or ``None`` when unavailable.

    Returning ``None`` indicates that hardware-dependent contract tests should skip.
    """


@hookspec
def pytest_pyvisa_command_map(
    config: pytest.Config,
    profile: InstrumentProfile | None,
) -> Mapping[str, str]:
    """Return semantic command mappings for contract tests.

    Hooks can return partial mappings; entries are merged in plugin registration order.
    """


@hookspec
def pytest_pyvisa_backend_capabilities(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> Mapping[str, bool]:
    """Return backend capability flags used by shared contract tests.

    Hooks can return partial mappings; entries are merged in plugin registration order.
    """


@hookspec
def pytest_pyvisa_contract_exclusions(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> Sequence[tuple[str, str]]:
    """Return contract exclusions as ``(contract_id, reason)`` tuples.

    Contract tests can interpret entries as skip/xfail declarations.
    """
