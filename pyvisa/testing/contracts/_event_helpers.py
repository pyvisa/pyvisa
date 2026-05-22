# -*- coding: utf-8 -*-
"""Internal helpers shared by event-oriented contract tests."""

from __future__ import annotations

import ctypes


def compare_user_handle(handle_a, handle_b) -> bool:
    """Compare user handles passed through VISA callback APIs."""
    if isinstance(handle_a, ctypes.Structure):
        return handle_a == handle_b
    if hasattr(handle_a, "value"):
        return handle_a.value == handle_b.value
    if isinstance(handle_a, (tuple, list)):
        return all(i == j for i, j in zip(handle_a, handle_b))
    return handle_a == handle_b
