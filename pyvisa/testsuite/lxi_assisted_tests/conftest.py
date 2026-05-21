# -*- coding: utf-8 -*-
"""Pytest fixtures for lxi-assisted tests."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pytest

from .env_helpers import discover_env_file, load_lxi_env_from_file


_LOADED_ENV = load_lxi_env_from_file()


@pytest.fixture(scope="session")
def lxi_env_file_path() -> Optional[Path]:
    """Path to the loaded env file, if any."""
    return discover_env_file()


@pytest.fixture(scope="session")
def lxi_env_entries() -> Dict[str, str]:
    """Environment entries loaded from file."""
    return dict(_LOADED_ENV)
