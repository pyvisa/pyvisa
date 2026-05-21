# -*- coding: utf-8 -*-
"""Helpers to populate PYVISA_LXI_* settings from an env file."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional


def discover_env_file() -> Optional[Path]:
    """Find an env file path for lxi-assisted test configuration."""
    explicit = os.environ.get("PYVISA_LXI_ENV_FILE")
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_file():
            return path
        return None

    for candidate in (Path("lxi.env"), Path(".lxi.env")):
        if candidate.is_file():
            return candidate

    return None


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse KEY=VALUE lines from an env file."""
    result: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        result[key] = value.strip()
    return result


def load_lxi_env_from_file() -> Dict[str, str]:
    """Load PYVISA_LXI_* values from a discovered env file.

    Existing environment variables are kept as-is.
    """
    path = discover_env_file()
    if path is None:
        return {}

    loaded = parse_env_file(path)
    for key, value in loaded.items():
        if not key.startswith("PYVISA_LXI_"):
            continue
        os.environ.setdefault(key, value)

    os.environ.setdefault("PYVISA_LXI_ENV_FILE", str(path.resolve()))
    return loaded
