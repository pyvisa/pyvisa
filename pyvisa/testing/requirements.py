# -*- coding: utf-8 -*-
"""Shared pytest requirement markers for reusable backend contracts."""

from __future__ import annotations

import pytest

from pyvisa import ResourceManager

try:
    ResourceManager()
except ValueError:
    VISA_PRESENT = False
else:
    VISA_PRESENT = True

require_visa_lib = pytest.mark.skipif(
    not VISA_PRESENT,
    reason="Requires an installed VISA library.",
)
