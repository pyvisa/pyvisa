# -*- coding: utf-8 -*-
"""Pytest hook specifications for PyVISA shared backend contracts."""

from __future__ import annotations

import pytest
from pluggy import HookspecMarker

from .pools import InstrumentPool
from .profiles import (
    CapabilityFlags,
    CommandMap,
    ContractExclusions,
    InstrumentProfile,
)
from .providers import ResourceManagerProvider

hookspec = HookspecMarker("pytest")


@hookspec(firstresult=True)
def pytest_pyvisa_select_profile(
    config: pytest.Config, profile_name: str
) -> InstrumentProfile | None:
    """Return the selected instrument profile, or ``None`` when unavailable.

    Returning ``None`` indicates that hardware-dependent contract tests should skip.
    """


@hookspec(firstresult=True)
def pytest_pyvisa_select_resource_manager_provider(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> ResourceManagerProvider | None:
    """Return the provider used to create ResourceManager instances.

    Returning ``None`` lets the shared plugin create the default provider for the
    selected backend identifier.
    """


@hookspec
def pytest_pyvisa_command_map(
    config: pytest.Config,
    profile: InstrumentProfile | None,
) -> CommandMap:
    """Return semantic command mappings for contract tests.

    Hooks can return partial mappings; entries are merged in plugin registration order.
    """


@hookspec(firstresult=True)
def pytest_pyvisa_select_instrument_pool(
    config: pytest.Config,
    profile: InstrumentProfile,
    command_map: CommandMap,
) -> InstrumentPool | None:
    """Return the instrument pool used by shared contracts.

    Returning ``None`` lets the shared plugin create a default command-map-backed
    pool from the selected profile.
    """


@hookspec
def pytest_pyvisa_backend_capabilities(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> CapabilityFlags:
    """Return backend capability flags used by shared contract tests.

    Hooks can return partial mappings; entries are merged in plugin registration order.
    """


@hookspec
def pytest_pyvisa_contract_exclusions(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> ContractExclusions:
    """Return contract exclusions keyed by contract identifier.

    Contract tests can interpret entries as skip/xfail declarations.
    """
