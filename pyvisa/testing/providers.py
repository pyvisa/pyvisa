# -*- coding: utf-8 -*-
"""Resource-manager provider abstractions for shared backend contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .profiles import CapabilityFlags, ProfileMetadata


@dataclass(frozen=True)
class ResourceManagerProvider(ABC):
    """Describe how shared contracts should create a ResourceManager.

    Providers are the framework-owned source of backend capabilities for skip
    and policy logic. Instrument-side capabilities still come from profiles and,
    later, instrument pools.
    """

    name: str
    backend_id: str
    backend_capabilities: CapabilityFlags = field(default_factory=CapabilityFlags)
    ignores_standard_env: bool = False
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)

    def __post_init__(self) -> None:
        if not isinstance(self.backend_capabilities, CapabilityFlags):
            object.__setattr__(
                self,
                "backend_capabilities",
                CapabilityFlags(self.backend_capabilities),
            )
        if not isinstance(self.metadata, ProfileMetadata):
            object.__setattr__(
                self,
                "metadata",
                ProfileMetadata.from_mapping(self.metadata),
            )

    @abstractmethod
    def resource_manager_specification(self) -> str:
        """Return the ResourceManager specification string."""

    def create_resource_manager(self):
        """Create a ResourceManager using the provider specification."""
        from pyvisa import ResourceManager

        return ResourceManager(self.resource_manager_specification())


@dataclass(frozen=True)
class StaticResourceManagerProvider(ResourceManagerProvider):
    """Provider backed by a static ResourceManager specification string."""

    specification: str = ""

    def resource_manager_specification(self) -> str:
        return self.specification


@dataclass(frozen=True)
class IVIResourceManagerProvider(StaticResourceManagerProvider):
    """Explicit IVI provider that does not inherit PYVISA_LIBRARY defaults."""

    name: str = "ivi"
    backend_id: str = "ivi"
    ignores_standard_env: bool = True
    specification: str = "@ivi"

    @classmethod
    def from_library_path(
        cls,
        visa_library_path: str = "",
        backend_capabilities: CapabilityFlags | None = None,
        metadata: ProfileMetadata | None = None,
    ) -> "IVIResourceManagerProvider":
        specification = f"{visa_library_path}@ivi" if visa_library_path else "@ivi"
        return cls(
            specification=specification,
            backend_capabilities=backend_capabilities or CapabilityFlags(),
            metadata=metadata or ProfileMetadata(),
        )


def default_resource_manager_provider(
    backend_id: str,
    *,
    ivi_library_path: str = "",
    backend_capabilities: CapabilityFlags | None = None,
    metadata: ProfileMetadata | None = None,
) -> ResourceManagerProvider:
    """Build the default provider used when no plugin contributes one."""
    if backend_id == "ivi":
        return IVIResourceManagerProvider.from_library_path(
            ivi_library_path,
            backend_capabilities=backend_capabilities,
            metadata=metadata,
        )

    specification = f"@{backend_id}" if backend_id else ""
    return StaticResourceManagerProvider(
        name=backend_id or "default",
        backend_id=backend_id,
        backend_capabilities=backend_capabilities or CapabilityFlags(),
        ignores_standard_env=bool(specification),
        metadata=metadata or ProfileMetadata(),
        specification=specification,
    )
