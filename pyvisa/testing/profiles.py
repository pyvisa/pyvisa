# -*- coding: utf-8 -*-
"""Data models used by shared backend contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping, TypeVar, cast

_RESOURCE_KEY_TO_ATTR = {
    "TCPIP::INSTR": "tcpip_instr",
    "TCPIP::HISLIP": "tcpip_hislip",
    "TCPIP::SOCKET": "tcpip_socket",
    "USB::INSTR": "usb_instr",
    "GPIB::INSTR": "gpib_instr",
    "GPIB::INTFC": "gpib_intfc",
    "ASRL::INSTR": "asrl_instr",
}

_COMMAND_KEY_TO_ATTR = {
    "identity_query": "identity_query",
    "shared_query": "shared_query",
    "health_query": "health_query",
    "error_query": "error_query",
    "binary_query_template": "binary_query_template",
    "binary_configure_template": "binary_configure_template",
    "binary_read_query": "binary_read_query",
    "srq_payload": "srq_payload",
    "srq_expected_read": "srq_expected_read",
    "srq_arm": "srq_arm",
    "srq_trigger": "srq_trigger",
    "srq_clear": "srq_clear",
}

_RESOURCE_KEY_TO_CAPABILITY_ROUTE = {
    "TCPIP::INSTR": ("tcpip", "vxi11"),
    "TCPIP::HISLIP": ("tcpip", "hislip"),
    "TCPIP::SOCKET": ("tcpip", "socket"),
    "USB::INSTR": ("usb", None),
    "GPIB::INSTR": ("gpib", "instr"),
    "GPIB::INTFC": ("gpib", "intfc"),
    "ASRL::INSTR": ("asrl", None),
}


@dataclass(frozen=True)
class ResourceAddresses:
    """Explicit address fields used by shared resource contracts."""

    tcpip_instr: str | None = None
    tcpip_hislip: str | None = None
    tcpip_socket: str | None = None
    usb_instr: str | None = None
    gpib_instr: str | None = None
    gpib_intfc: str | None = None
    asrl_instr: str | None = None
    extras: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, str]) -> "ResourceAddresses":
        values = dict(mapping)
        fields: dict[str, str | None] = {}
        for key, attr_name in _RESOURCE_KEY_TO_ATTR.items():
            fields[attr_name] = values.pop(key, None)
        return cls(extras=values, **fields)

    def for_resource(self, resource_key: str) -> str | None:
        attr_name = _RESOURCE_KEY_TO_ATTR.get(resource_key)
        if attr_name is not None:
            return getattr(self, attr_name)
        return self.extras.get(resource_key)

    def items(self) -> list[tuple[str, str]]:
        values = []
        for key, attr_name in _RESOURCE_KEY_TO_ATTR.items():
            resource = getattr(self, attr_name)
            if resource:
                values.append((key, resource))
        values.extend((k, v) for k, v in self.extras.items() if v)
        return values

    def to_dict(self) -> dict[str, str]:
        return dict(self.items())


@dataclass(frozen=True)
class CommandMap:
    """Explicit command semantics for shared resource contracts."""

    identity_query: str | None = None
    shared_query: str | None = None
    health_query: str | None = None
    error_query: str | None = None
    binary_query_template: str | None = None
    binary_configure_template: str | None = None
    binary_read_query: str | None = None
    srq_payload: str | None = None
    srq_expected_read: str | None = None
    srq_arm: str | None = None
    srq_trigger: str | None = None
    srq_clear: str | None = None
    extras: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, str]) -> "CommandMap":
        values = dict(mapping)
        fields: dict[str, str | None] = {}
        for key, attr_name in _COMMAND_KEY_TO_ATTR.items():
            fields[attr_name] = values.pop(key, None)
        return cls(extras=values, **fields)

    def require(self, command_key: str) -> str:
        attr_name = _COMMAND_KEY_TO_ATTR.get(command_key)
        value: str | None
        if attr_name is None:
            value = self.extras.get(command_key)
        else:
            value = getattr(self, attr_name)
        if value is None:
            raise KeyError(command_key)
        return value

    def to_dict(self) -> dict[str, str]:
        values = dict(self.extras)
        for key, attr_name in _COMMAND_KEY_TO_ATTR.items():
            value = getattr(self, attr_name)
            if value is not None:
                values[key] = value
        return values

    def overlay(self, other: "CommandMap") -> "CommandMap":
        merged = self.to_dict()
        merged.update(other.to_dict())
        return CommandMap.from_mapping(merged)


@dataclass(frozen=True)
class BaseResourceCapabilities:
    """Common feature toggles shared by resource-class capability types."""

    supported: bool | None = None
    query: bool | None = None
    timeout: bool | None = None
    locking: bool | None = None
    trigger: bool | None = None
    read_stb: bool | None = None
    srq_queue: bool | None = None
    srq_handler: bool | None = None

    def feature(self, name: str, default: bool = False) -> bool:
        value = getattr(self, name, None)
        return default if value is None else bool(value)

    def overlay(self, other: "BaseResourceCapabilities") -> "BaseResourceCapabilities":
        if type(self) is not type(other):
            raise TypeError(
                "Cannot overlay capabilities from different resource classes"
            )
        merged: dict[str, Any] = {}
        for field_name in self.__dataclass_fields__:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)
            merged[field_name] = self_value if other_value is None else other_value
        return type(self)(**merged)


@dataclass(frozen=True)
class MessageBasedResourceCapabilities(BaseResourceCapabilities):
    """Capabilities shared by message-based resources."""


@dataclass(frozen=True)
class UsbResourceCapabilities(MessageBasedResourceCapabilities):
    """USB-specific resource capability toggles."""

    control_transfer: bool | None = None
    attributes: bool | None = None


@dataclass(frozen=True)
class GpibInterfaceCapabilities(BaseResourceCapabilities):
    """GPIB interface-class capability toggles."""

    bus_control: bool | None = None
    controller_ops: bool | None = None


@dataclass(frozen=True)
class AsrlResourceCapabilities(BaseResourceCapabilities):
    """ASRL-specific capability toggles."""


_CapabilityT = TypeVar("_CapabilityT", bound="BaseResourceCapabilities")


def _overlay_resource_caps(
    base: _CapabilityT | None,
    override: _CapabilityT | None,
) -> _CapabilityT | None:
    if override is None:
        return base
    if base is None:
        return override
    return cast(_CapabilityT, base.overlay(override))


@dataclass(frozen=True)
class TcpipCapabilities:
    """Capabilities grouped for TCPIP resource families."""

    vxi11: MessageBasedResourceCapabilities | None = None
    hislip: MessageBasedResourceCapabilities | None = None
    socket: MessageBasedResourceCapabilities | None = None

    def transport_enabled_for_member(self, member: str, default: bool = True) -> bool:
        caps = self.capabilities_for_member(member)
        if caps is None:
            return default
        if caps.supported is None:
            return True
        return bool(caps.supported)

    def capabilities_for_member(
        self, member: str
    ) -> MessageBasedResourceCapabilities | None:
        if member == "vxi11":
            return self.vxi11
        if member == "hislip":
            return self.hislip
        if member == "socket":
            return self.socket
        raise KeyError(member)

    def overlay(self, other: "TcpipCapabilities") -> "TcpipCapabilities":
        return TcpipCapabilities(
            vxi11=_overlay_resource_caps(self.vxi11, other.vxi11),
            hislip=_overlay_resource_caps(self.hislip, other.hislip),
            socket=_overlay_resource_caps(self.socket, other.socket),
        )


@dataclass(frozen=True)
class GpibCapabilities:
    """Capabilities grouped for GPIB resource families."""

    enabled: bool | None = None
    instr: MessageBasedResourceCapabilities | None = None
    intfc: GpibInterfaceCapabilities | None = None

    def enabled_for_member(self, member: str, default: bool = True) -> bool:
        _ = member
        return default if self.enabled is None else bool(self.enabled)

    def capabilities_for_member(
        self,
        member: str,
    ) -> MessageBasedResourceCapabilities | GpibInterfaceCapabilities | None:
        if member == "instr":
            return self.instr
        if member == "intfc":
            return self.intfc
        raise KeyError(member)

    def overlay(self, other: "GpibCapabilities") -> "GpibCapabilities":
        return GpibCapabilities(
            enabled=self.enabled if other.enabled is None else other.enabled,
            instr=_overlay_resource_caps(self.instr, other.instr),
            intfc=_overlay_resource_caps(self.intfc, other.intfc),
        )


@dataclass(frozen=True)
class CapabilityFlags:
    """Domain-composed capability model used by shared contract skip logic."""

    tcpip: TcpipCapabilities | None = None
    gpib: GpibCapabilities | None = None
    usb: UsbResourceCapabilities | None = None
    asrl: AsrlResourceCapabilities | None = None

    def transport_enabled_for_resource(
        self, resource_key: str, default: bool = True
    ) -> bool:
        route = _RESOURCE_KEY_TO_CAPABILITY_ROUTE.get(resource_key)
        if route is None:
            raise KeyError(resource_key)

        domain_name, member_name = route
        if domain_name == "tcpip":
            if self.tcpip is None:
                return default
            assert member_name is not None
            return self.tcpip.transport_enabled_for_member(member_name, default)

        if domain_name == "gpib":
            if self.gpib is None:
                return default
            assert member_name is not None
            return self.gpib.enabled_for_member(member_name, default)

        if domain_name == "usb":
            if self.usb is None or self.usb.supported is None:
                return default
            return bool(self.usb.supported)

        if domain_name == "asrl":
            if self.asrl is None or self.asrl.supported is None:
                return default
            return bool(self.asrl.supported)

        raise KeyError(resource_key)

    def resource_capabilities(
        self, resource_key: str
    ) -> BaseResourceCapabilities | None:
        route = _RESOURCE_KEY_TO_CAPABILITY_ROUTE.get(resource_key)
        if route is None:
            raise KeyError(resource_key)

        domain_name, member_name = route
        if domain_name == "tcpip":
            if self.tcpip is None:
                return None
            assert member_name is not None
            return self.tcpip.capabilities_for_member(member_name)

        if domain_name == "gpib":
            if self.gpib is None:
                return None
            assert member_name is not None
            return self.gpib.capabilities_for_member(member_name)

        if domain_name == "usb":
            return self.usb

        if domain_name == "asrl":
            return self.asrl

        raise KeyError(resource_key)

    def resource_feature(
        self, resource_key: str, feature: str, default: bool = True
    ) -> bool:
        caps = self.resource_capabilities(resource_key)
        if caps is None:
            return default
        return caps.feature(feature, default)

    def overlay(self, other: "CapabilityFlags") -> "CapabilityFlags":
        if other.tcpip is None:
            tcpip = self.tcpip
        elif self.tcpip is None:
            tcpip = other.tcpip
        else:
            tcpip = self.tcpip.overlay(other.tcpip)

        if other.gpib is None:
            gpib = self.gpib
        elif self.gpib is None:
            gpib = other.gpib
        else:
            gpib = self.gpib.overlay(other.gpib)

        usb = _overlay_resource_caps(self.usb, other.usb)
        asrl = _overlay_resource_caps(self.asrl, other.asrl)

        return CapabilityFlags(
            tcpip=tcpip,
            gpib=gpib,
            usb=usb,
            asrl=asrl,
        )


@dataclass(frozen=True)
class ProfileMetadata:
    """Typed profile metadata with canonical top-level fields."""

    source: str | None = None
    target: str | None = None
    backend: str | None = None
    extras: Mapping[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        if key == "source":
            return self.source if self.source is not None else default
        if key == "target":
            return self.target if self.target is not None else default
        if key == "backend":
            return self.backend if self.backend is not None else default
        return self.extras.get(key, default)

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

    def with_updates(
        self,
        *,
        source: str | None = None,
        target: str | None = None,
        backend: str | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> "ProfileMetadata":
        return ProfileMetadata(
            source=self.source if source is None else source,
            target=self.target if target is None else target,
            backend=self.backend if backend is None else backend,
            extras=dict(self.extras) if extras is None else extras,
        )


@dataclass(frozen=True)
class ContractExclusion:
    """Structured exclusion entry for one shared contract identifier."""

    contract_id: str
    reason: str


@dataclass(frozen=True)
class ContractExclusions:
    """Typed container for contract exclusion reasons by contract id."""

    values: Mapping[str, str] = field(default_factory=dict)

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)

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
            raise TypeError("resource_addresses must be a ResourceAddresses instance")
        if not isinstance(self.command_map, CommandMap):
            raise TypeError("command_map must be a CommandMap instance")
        if not isinstance(self.capabilities, CapabilityFlags):
            raise TypeError("capabilities must be a CapabilityFlags instance")
        if not isinstance(self.metadata, ProfileMetadata):
            raise TypeError("metadata must be a ProfileMetadata instance")
