# -*- coding: utf-8 -*-
"""Global pytest configuration for the top-level PyVISA test tree."""

from __future__ import annotations

import pytest

from pyvisa.testing import InstrumentProfile

from .keysight_assisted_tests.conftest import keysight_profile_from_env
from .pyvisa_tester_assisted_tests.config import build_pyvisa_tester_profile

pytest_plugins = ("pyvisa.testing.pytest_plugin",)


@pytest.hookimpl(tryfirst=True)
def pytest_pyvisa_select_profile(
    config: pytest.Config, profile_name: str
) -> InstrumentProfile | None:
    """Provide pyvisa-owned profile selection with code-first defaults."""
    _ = config
    if profile_name == "keysight":
        return keysight_profile_from_env()

    if profile_name == "env":
        return keysight_profile_from_env() or build_pyvisa_tester_profile()

    if profile_name == "pyvisa-tester":
        return build_pyvisa_tester_profile()

    if profile_name == "keysight-or-tester":
        return keysight_profile_from_env() or build_pyvisa_tester_profile()

    return None
