# -*- coding: utf-8 -*-
"""Helpers for explicit command-map resolution in shared contracts."""

from __future__ import annotations

import pytest

from pyvisa.testing import CommandMap


def require_command(command_map: CommandMap, command_key: str) -> str:
    """Return a required semantic command or fail with a clear message."""
    try:
        return command_map.require(command_key)
    except KeyError as exc:
        pytest.fail(
            f"Missing required command mapping {command_key!r} in pyvisa_command_map"
        )
        raise AssertionError("unreachable") from exc
