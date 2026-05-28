# -*- coding: utf-8 -*-
"""Unit tests for shared testing provider models."""

from __future__ import annotations

import pytest

from pyvisa.testing import CapabilityFlags, ProfileMetadata
from pyvisa.testing.providers import StaticResourceManagerProvider


def test_static_provider_accepts_typed_capabilities_and_metadata():
    provider = StaticResourceManagerProvider(
        name="py",
        backend_id="py",
        backend_capabilities=CapabilityFlags(events_srq=True),
        metadata=ProfileMetadata(target="pyvisa-tester"),
        specification="@py",
    )

    assert provider.backend_capabilities.events_srq is True
    assert provider.metadata.target == "pyvisa-tester"


def test_static_provider_rejects_non_capability_flags():
    with pytest.raises(TypeError, match="backend_capabilities"):
        StaticResourceManagerProvider(
            name="py",
            backend_id="py",
            backend_capabilities={"events.srq": True},
            metadata=ProfileMetadata(target="pyvisa-tester"),
            specification="@py",
        )


def test_static_provider_rejects_non_metadata():
    with pytest.raises(TypeError, match="metadata"):
        StaticResourceManagerProvider(
            name="py",
            backend_id="py",
            backend_capabilities=CapabilityFlags(events_srq=True),
            metadata={"target": "pyvisa-tester"},
            specification="@py",
        )
