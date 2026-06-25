# -*- coding: utf-8 -*-
"""Pytest plugin for PyVISA shared backend contract tests."""

from __future__ import annotations

import pytest

from . import hookspec
from .env_profile import profile_from_environment
from .pools import InstrumentPool, build_default_instrument_pool
from .profiles import (
    CapabilityFlags,
    CommandMap,
    ContractExclusions,
    InstrumentProfile,
)
from .providers import ResourceManagerProvider, default_resource_manager_provider

DEFAULT_COMMAND_MAP = CommandMap(
    identity_query="*IDN?",
    shared_query="QUERY?",
    health_query="SYST:HEALTH?",
    error_query="SYST:ERR?",
    binary_query_template="DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    binary_configure_template="DATA:BIN:CFG {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    binary_read_query="DATA:BIN:READ?",
    srq_payload="DATA:PAYLOAD 1",
    srq_expected_read="1",
    srq_arm="EVEN:SRQ:ARM 1",
    srq_trigger="EVEN:SRQ:TRIG",
    srq_clear="EVEN:SRQ:CLE",
)


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """Register custom hook specifications for backend test contracts."""
    pluginmanager.add_hookspecs(hookspec)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Expose command-line controls for shared backend contracts."""
    group = parser.getgroup("pyvisa-contracts")
    group.addoption(
        "--pyvisa-profile",
        action="store",
        default="env",
        help="Name of the profile to use for shared hardware contract tests.",
    )
    group.addoption(
        "--pyvisa-backend-id",
        action="store",
        default="ivi",
        help="Backend identifier used by capability hooks (for example ivi, py).",
    )
    group.addoption(
        "--pyvisa-ivi-library",
        action="store",
        default="",
        help="Explicit IVI library path used by the default IVI provider.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Declare markers used by shared contract tests."""
    config.addinivalue_line(
        "markers",
        "pyvisa_contract: Marks tests that belong to shared backend contracts.",
    )
    config.addinivalue_line(
        "markers",
        "pyvisa_hardware: Marks tests requiring an instrument profile.",
    )


@pytest.hookimpl(trylast=True)
def pytest_pyvisa_select_profile(
    config: pytest.Config, profile_name: str
) -> InstrumentProfile | None:
    """Default profile provider based on PYVISA_TESTER_* environment values."""
    _ = config
    if profile_name != "env":
        return None
    return profile_from_environment()


def _selected_backend_id(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("--pyvisa-backend-id"))


@pytest.fixture(scope="session")
def pyvisa_resource_manager_provider(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
) -> ResourceManagerProvider:
    """Provider used by shared contracts to create ResourceManager instances."""
    backend_id = _selected_backend_id(pytestconfig)
    provider = pytestconfig.hook.pytest_pyvisa_select_resource_manager_provider(
        config=pytestconfig,
        backend_id=backend_id,
        profile=pyvisa_profile,
    )
    if provider is not None:
        return provider

    return default_resource_manager_provider(
        backend_id,
        ivi_library_path=str(pytestconfig.getoption("--pyvisa-ivi-library")),
    )


@pytest.fixture
def pyvisa_resource_manager(pyvisa_resource_manager_provider: ResourceManagerProvider):
    """ResourceManager created through the selected provider."""
    rm = pyvisa_resource_manager_provider.create_resource_manager()
    try:
        yield rm
    finally:
        rm.close()


@pytest.hookimpl(trylast=True)
def pytest_pyvisa_command_map(
    config: pytest.Config,
    profile: InstrumentProfile | None,
) -> CommandMap:
    """Provide default semantic command mappings."""
    _ = config
    if profile is None:
        return CommandMap()

    return DEFAULT_COMMAND_MAP.overlay(profile.command_map)


@pytest.fixture(scope="session")
def pyvisa_profile(pytestconfig: pytest.Config) -> InstrumentProfile | None:
    """Selected instrument profile used by contract tests."""
    profile_name = str(pytestconfig.getoption("--pyvisa-profile"))
    return pytestconfig.hook.pytest_pyvisa_select_profile(
        config=pytestconfig, profile_name=profile_name
    )


@pytest.fixture(scope="session")
def pyvisa_command_map(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
) -> CommandMap:
    """Merged semantic command mapping provided by plugins."""
    merged = CommandMap()
    results = pytestconfig.hook.pytest_pyvisa_command_map(
        config=pytestconfig, profile=pyvisa_profile
    )
    for mapping in results:
        merged = merged.overlay(mapping)
    return merged


@pytest.fixture(scope="session")
def pyvisa_instrument_pool(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
    pyvisa_command_map: CommandMap,
) -> InstrumentPool:
    """Instrument pool used by shared contracts."""
    if pyvisa_profile is None:
        pytest.skip(
            "No instrument profile available to build an instrument pool. "
            "Configure a shared test profile or plugin provider."
        )

    pool = pytestconfig.hook.pytest_pyvisa_select_instrument_pool(
        config=pytestconfig,
        profile=pyvisa_profile,
        command_map=pyvisa_command_map,
    )
    if pool is not None:
        return pool

    return build_default_instrument_pool(pyvisa_profile, pyvisa_command_map)


@pytest.fixture(scope="session")
def pyvisa_backend_capabilities(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
    pyvisa_resource_manager_provider: ResourceManagerProvider,
) -> CapabilityFlags:
    """Merged backend capability map used by contract tests."""
    backend_id = _selected_backend_id(pytestconfig)
    merged = pyvisa_resource_manager_provider.backend_capabilities
    results = pytestconfig.hook.pytest_pyvisa_backend_capabilities(
        config=pytestconfig,
        backend_id=backend_id,
        profile=pyvisa_profile,
    )
    for mapping in results:
        merged = merged.overlay(mapping)

    if pyvisa_profile is not None:
        merged = merged.overlay(pyvisa_profile.capabilities)

    return merged


@pytest.fixture(scope="session")
def pyvisa_contract_exclusions(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
) -> ContractExclusions:
    """Contract exclusions declared by backend plugins."""
    backend_id = _selected_backend_id(pytestconfig)
    exclusions: dict[str, str] = {}
    results = pytestconfig.hook.pytest_pyvisa_contract_exclusions(
        config=pytestconfig,
        backend_id=backend_id,
        profile=pyvisa_profile,
    )
    for entries in results:
        exclusions.update(entries.to_dict())
    return ContractExclusions(exclusions)


@pytest.fixture
def apply_pyvisa_contract_policy(pyvisa_contract_exclusions: ContractExclusions):
    """Apply hook-declared contract exclusions by contract identifier."""

    def _apply(contract_id: str) -> None:
        reason = pyvisa_contract_exclusions.get(contract_id)
        if reason:
            pytest.xfail(reason)

    return _apply


@pytest.fixture
def require_pyvisa_profile(
    pyvisa_profile: InstrumentProfile | None,
) -> InstrumentProfile:
    """Skip when no hardware profile is available."""
    if pyvisa_profile is None:
        pytest.skip(
            "No instrument profile available. Configure PYVISA_TESTER_ASSISTED=1 and "
            "PYVISA_TESTER_* settings or provide a plugin hook for --pyvisa-profile."
        )
    return pyvisa_profile


def pytest_pyvisa_select_instrument_pool(
    config: pytest.Config,
    profile: InstrumentProfile,
    command_map: CommandMap,
) -> InstrumentPool | None:
    """Default pool fallback used when no plugin contributes one."""
    _ = config
    return build_default_instrument_pool(profile, command_map)


def pytest_pyvisa_select_resource_manager_provider(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> ResourceManagerProvider | None:
    """Default provider fallback used when no plugin contributes one."""
    _ = (config, profile)
    return default_resource_manager_provider(backend_id)


def pytest_pyvisa_backend_capabilities(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> CapabilityFlags:
    """Default capability fallback used when no backend plugin contributes flags."""
    _ = (config, backend_id, profile)
    return CapabilityFlags()


def pytest_pyvisa_contract_exclusions(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> ContractExclusions:
    """Default exclusion fallback used when no backend plugin contributes entries."""
    _ = (config, backend_id, profile)
    return ContractExclusions()
