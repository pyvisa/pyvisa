# -*- coding: utf-8 -*-
"""Data models used by shared backend contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping


@dataclass(frozen=True)
class ResourceAddresses(Mapping[str, str]):
    """Typed container for resource class to VISA address mappings."""

    values: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", dict(self.values))

    def __getitem__(self, key: str) -> str:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def to_dict(self) -> dict[str, str]:
        """Return a mutable copy of the addresses."""
        return dict(self.values)


@dataclass(frozen=True)
class CommandMap(Mapping[str, str]):
    """Typed container for semantic command-name mappings."""

    values: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", dict(self.values))

    def __getitem__(self, key: str) -> str:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def to_dict(self) -> dict[str, str]:
        """Return a mutable copy of the command mapping."""
        return dict(self.values)


@dataclass(frozen=True)
class CapabilityFlags(Mapping[str, bool]):
    """Typed container for backend/profile capability flags."""

    values: Mapping[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", {k: bool(v) for k, v in self.values.items()})

    def __getitem__(self, key: str) -> bool:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def to_dict(self) -> dict[str, bool]:
        """Return a mutable copy of capability flags."""
        return dict(self.values)


@dataclass(frozen=True)
class ProfileMetadata(Mapping[str, Any]):
    """Typed profile metadata with canonical top-level fields."""

    source: str | None = None
    target: str | None = None
    backend: str | None = None
    extras: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "extras", dict(self.extras))

    def __getitem__(self, key: str) -> Any:
        if key == "source" and self.source is not None:
            return self.source
        if key == "target" and self.target is not None:
            return self.target
        if key == "backend" and self.backend is not None:
            return self.backend
        return self.extras[key]

    def __iter__(self) -> Iterator[str]:
        if self.source is not None:
            yield "source"
        if self.target is not None:
            yield "target"
        if self.backend is not None:
            yield "backend"
        for key in self.extras:
            if key not in {"source", "target", "backend"}:
                yield key

    def __len__(self) -> int:
        count = len(self.extras)
        if self.source is not None and "source" not in self.extras:
            count += 1
        if self.target is not None and "target" not in self.extras:
            count += 1
        if self.backend is not None and "backend" not in self.extras:
            count += 1
        return count

    def to_dict(self) -> dict[str, Any]:
        """Return metadata as a plain dictionary."""
        data = dict(self.extras)
        if self.source is not None:
            data["source"] = self.source
        if self.target is not None:
            data["target"] = self.target
        if self.backend is not None:
            data["backend"] = self.backend
        return data

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "ProfileMetadata":
        """Build metadata from a plain mapping."""
        extras = {
            key: value
            for key, value in mapping.items()
            if key not in {"source", "target", "backend"}
        }
        source = mapping.get("source")
        target = mapping.get("target")
        backend = mapping.get("backend")
        return cls(
            source=str(source) if source is not None else None,
            target=str(target) if target is not None else None,
            backend=str(backend) if backend is not None else None,
            extras=extras,
        )


@dataclass(frozen=True)
class ContractExclusion:
    """Structured exclusion entry for one shared contract identifier."""

    contract_id: str
    reason: str


@dataclass(frozen=True)
class ContractExclusions(Mapping[str, str]):
    """Typed container for contract exclusion reasons by contract id."""

    values: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            {str(key): str(value) for key, value in self.values.items()},
        )

    def __getitem__(self, key: str) -> str:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def to_dict(self) -> dict[str, str]:
        """Return exclusions as a plain dictionary."""
        return dict(self.values)

    @classmethod
    def from_entries(
        cls, entries: Iterator[ContractExclusion] | list[ContractExclusion]
    ) -> "ContractExclusions":
        """Build exclusions from structured entries."""
        return cls({entry.contract_id: entry.reason for entry in entries})


@dataclass(frozen=True)
class InstrumentProfile:
    """Resolved target used to run contract tests.

    Attributes
    ----------
    name:
        Human-friendly profile name.
    resource_addresses:
        Mapping from abstract resource kinds to VISA resource strings.
        Typical keys: TCPIP::INSTR, TCPIP::HISLIP, TCPIP::SOCKET, USB::INSTR.
    expected_idn:
        Optional value expected by identity tests.
    command_map:
        Semantic command identifiers mapped to concrete instrument commands.
    capabilities:
        Capability flags used by tests to decide which checks to execute.
    metadata:
        Optional additional context attached by profile providers.
    """

    name: str
    resource_addresses: ResourceAddresses = field(default_factory=ResourceAddresses)
    expected_idn: str | None = None
    command_map: CommandMap = field(default_factory=CommandMap)
    capabilities: CapabilityFlags = field(default_factory=CapabilityFlags)
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)

    def __post_init__(self) -> None:
        if not isinstance(self.resource_addresses, ResourceAddresses):
            object.__setattr__(
                self,
                "resource_addresses",
                ResourceAddresses(self.resource_addresses),
            )
        if not isinstance(self.command_map, CommandMap):
            object.__setattr__(
                self,
                "command_map",
                CommandMap(self.command_map),
            )
        if not isinstance(self.capabilities, CapabilityFlags):
            object.__setattr__(
                self,
                "capabilities",
                CapabilityFlags(self.capabilities),
            )
        if not isinstance(self.metadata, ProfileMetadata):
            object.__setattr__(
                self,
                "metadata",
                ProfileMetadata.from_mapping(self.metadata),
            )
