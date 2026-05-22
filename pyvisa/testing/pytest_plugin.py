# -*- coding: utf-8 -*-
"""Pytest plugin for PyVISA shared backend contract tests."""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from . import hookspec
from .env_profile import profile_from_environment
from .profiles import InstrumentProfile

DEFAULT_COMMAND_MAP = {
    "identity_query": "*IDN?",
    "shared_query": "QUERY?",
    "health_query": "SYST:HEALTH?",
    "binary_query_template": "DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}",
    "srq_payload": "DATA:PAYLOAD 1",
    "srq_expected_read": "1",
    "srq_arm": "EVEN:SRQ:ARM 1",
    "srq_trigger": "EVEN:SRQ:TRIG",
    "srq_clear": "EVEN:SRQ:CLE",
}


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


@pytest.hookimpl(trylast=True)
def pytest_pyvisa_command_map(
    config: pytest.Config,
    profile: InstrumentProfile | None,
) -> Mapping[str, str]:
    """Provide default semantic command mappings."""
    _ = config
    if profile is None:
        return {}

    merged = dict(DEFAULT_COMMAND_MAP)
    merged.update(profile.command_map)
    return merged


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
) -> dict[str, str]:
    """Merged semantic command mapping provided by plugins."""
    merged: dict[str, str] = {}
    results = pytestconfig.hook.pytest_pyvisa_command_map(
        config=pytestconfig, profile=pyvisa_profile
    )
    for mapping in results:
        merged.update(dict(mapping))
    return merged


@pytest.fixture(scope="session")
def pyvisa_backend_capabilities(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
) -> dict[str, bool]:
    """Merged backend capability map used by contract tests."""
    backend_id = str(pytestconfig.getoption("--pyvisa-backend-id"))
    merged: dict[str, bool] = {}
    results = pytestconfig.hook.pytest_pyvisa_backend_capabilities(
        config=pytestconfig,
        backend_id=backend_id,
        profile=pyvisa_profile,
    )
    for mapping in results:
        merged.update({key: bool(value) for key, value in dict(mapping).items()})

    if pyvisa_profile is not None:
        merged.update({k: bool(v) for k, v in pyvisa_profile.capabilities.items()})

    return merged


@pytest.fixture(scope="session")
def pyvisa_contract_exclusions(
    pytestconfig: pytest.Config,
    pyvisa_profile: InstrumentProfile | None,
) -> dict[str, str]:
    """Contract exclusions declared by backend plugins."""
    backend_id = str(pytestconfig.getoption("--pyvisa-backend-id"))
    exclusions: dict[str, str] = {}
    results = pytestconfig.hook.pytest_pyvisa_contract_exclusions(
        config=pytestconfig,
        backend_id=backend_id,
        profile=pyvisa_profile,
    )
    for entries in results:
        for contract_id, reason in entries:
            exclusions[str(contract_id)] = str(reason)
    return exclusions


@pytest.fixture
def apply_pyvisa_contract_policy(pyvisa_contract_exclusions: dict[str, str]):
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


def pytest_pyvisa_backend_capabilities(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> Mapping[str, bool]:
    """Default capability fallback used when no backend plugin contributes flags."""
    _ = (config, backend_id, profile)
    return {}


def pytest_pyvisa_contract_exclusions(
    config: pytest.Config,
    backend_id: str,
    profile: InstrumentProfile | None,
) -> list[tuple[str, str]]:
    """Default exclusion fallback used when no backend plugin contributes entries."""
    _ = (config, backend_id, profile)
    return []
