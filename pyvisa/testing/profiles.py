# -*- coding: utf-8 -*-
"""Data models used by shared backend contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping

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

_CAPABILITY_KEY_TO_ATTR = {
    "transport.vxi11": "transport_vxi11",
    "transport.hislip": "transport_hislip",
    "transport.socket": "transport_socket",
    "transport.usb": "transport_usb",
    "transport.gpib": "transport_gpib",
    "transport.asrl": "transport_asrl",
    "resource.query.tcpip.instr": "resource_query_tcpip_instr",
    "resource.query.tcpip.hislip": "resource_query_tcpip_hislip",
    "resource.query.tcpip.socket": "resource_query_tcpip_socket",
    "resource.query.usb.instr": "resource_query_usb_instr",
    "resource.query.gpib.instr": "resource_query_gpib_instr",
    "resource.query.gpib.intfc": "resource_query_gpib_intfc",
    "resource.query.asrl.instr": "resource_query_asrl_instr",
    "resource.gpib.intfc.query": "resource_gpib_intfc_query",
    "resource.timeout.tcpip.instr": "resource_timeout_tcpip_instr",
    "resource.timeout.tcpip.hislip": "resource_timeout_tcpip_hislip",
    "resource.timeout.tcpip.socket": "resource_timeout_tcpip_socket",
    "resource.timeout.usb.instr": "resource_timeout_usb_instr",
    "resource.timeout.gpib.instr": "resource_timeout_gpib_instr",
    "resource.timeout.gpib.intfc": "resource_timeout_gpib_intfc",
    "resource.timeout.asrl.instr": "resource_timeout_asrl_instr",
    "locking.shared": "locking_shared",
    "resource.locking.tcpip.instr": "resource_locking_tcpip_instr",
    "resource.locking.tcpip.hislip": "resource_locking_tcpip_hislip",
    "resource.locking.tcpip.socket": "resource_locking_tcpip_socket",
    "resource.locking.usb.instr": "resource_locking_usb_instr",
    "resource.locking.gpib.instr": "resource_locking_gpib_instr",
    "resource.locking.gpib.intfc": "resource_locking_gpib_intfc",
    "resource.locking.asrl.instr": "resource_locking_asrl_instr",
    "resource.trigger.tcpip.instr": "resource_trigger_tcpip_instr",
    "resource.trigger.tcpip.hislip": "resource_trigger_tcpip_hislip",
    "resource.trigger.tcpip.socket": "resource_trigger_tcpip_socket",
    "resource.trigger.usb.instr": "resource_trigger_usb_instr",
    "resource.trigger.gpib.instr": "resource_trigger_gpib_instr",
    "resource.trigger.gpib.intfc": "resource_trigger_gpib_intfc",
    "resource.trigger.asrl.instr": "resource_trigger_asrl_instr",
    "resource.read_stb.tcpip.instr": "resource_read_stb_tcpip_instr",
    "resource.read_stb.tcpip.hislip": "resource_read_stb_tcpip_hislip",
    "resource.read_stb.tcpip.socket": "resource_read_stb_tcpip_socket",
    "resource.read_stb.usb.instr": "resource_read_stb_usb_instr",
    "resource.read_stb.gpib.instr": "resource_read_stb_gpib_instr",
    "resource.read_stb.gpib.intfc": "resource_read_stb_gpib_intfc",
    "resource.read_stb.asrl.instr": "resource_read_stb_asrl_instr",
    "events.srq": "events_srq",
    "resource.event.srq.queue.tcpip.instr": "resource_event_srq_queue_tcpip_instr",
    "resource.event.srq.queue.tcpip.hislip": "resource_event_srq_queue_tcpip_hislip",
    "resource.event.srq.queue.tcpip.socket": "resource_event_srq_queue_tcpip_socket",
    "resource.event.srq.handler.tcpip.instr": "resource_event_srq_handler_tcpip_instr",
    "resource.event.srq.handler.tcpip.hislip": "resource_event_srq_handler_tcpip_hislip",
    "resource.event.srq.handler.tcpip.socket": "resource_event_srq_handler_tcpip_socket",
    "resource.usb.control_transfer": "resource_usb_control_transfer",
    "resource.usb.attributes": "resource_usb_attributes",
    "resource.gpib.intfc.bus_control": "resource_gpib_intfc_bus_control",
    "resource.gpib.intfc.controller_ops": "resource_gpib_intfc_controller_ops",
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
class CapabilityFlags:
    """Explicit capability semantics used by shared contract skip logic."""

    transport_vxi11: bool | None = None
    transport_hislip: bool | None = None
    transport_socket: bool | None = None
    transport_usb: bool | None = None
    transport_gpib: bool | None = None
    transport_asrl: bool | None = None
    resource_query_tcpip_instr: bool | None = None
    resource_query_tcpip_hislip: bool | None = None
    resource_query_tcpip_socket: bool | None = None
    resource_query_usb_instr: bool | None = None
    resource_query_gpib_instr: bool | None = None
    resource_query_gpib_intfc: bool | None = None
    resource_query_asrl_instr: bool | None = None
    resource_gpib_intfc_query: bool | None = None
    resource_timeout_tcpip_instr: bool | None = None
    resource_timeout_tcpip_hislip: bool | None = None
    resource_timeout_tcpip_socket: bool | None = None
    resource_timeout_usb_instr: bool | None = None
    resource_timeout_gpib_instr: bool | None = None
    resource_timeout_gpib_intfc: bool | None = None
    resource_timeout_asrl_instr: bool | None = None
    locking_shared: bool | None = None
    resource_locking_tcpip_instr: bool | None = None
    resource_locking_tcpip_hislip: bool | None = None
    resource_locking_tcpip_socket: bool | None = None
    resource_locking_usb_instr: bool | None = None
    resource_locking_gpib_instr: bool | None = None
    resource_locking_gpib_intfc: bool | None = None
    resource_locking_asrl_instr: bool | None = None
    resource_trigger_tcpip_instr: bool | None = None
    resource_trigger_tcpip_hislip: bool | None = None
    resource_trigger_tcpip_socket: bool | None = None
    resource_trigger_usb_instr: bool | None = None
    resource_trigger_gpib_instr: bool | None = None
    resource_trigger_gpib_intfc: bool | None = None
    resource_trigger_asrl_instr: bool | None = None
    resource_read_stb_tcpip_instr: bool | None = None
    resource_read_stb_tcpip_hislip: bool | None = None
    resource_read_stb_tcpip_socket: bool | None = None
    resource_read_stb_usb_instr: bool | None = None
    resource_read_stb_gpib_instr: bool | None = None
    resource_read_stb_gpib_intfc: bool | None = None
    resource_read_stb_asrl_instr: bool | None = None
    events_srq: bool | None = None
    resource_event_srq_queue_tcpip_instr: bool | None = None
    resource_event_srq_queue_tcpip_hislip: bool | None = None
    resource_event_srq_queue_tcpip_socket: bool | None = None
    resource_event_srq_handler_tcpip_instr: bool | None = None
    resource_event_srq_handler_tcpip_hislip: bool | None = None
    resource_event_srq_handler_tcpip_socket: bool | None = None
    resource_usb_control_transfer: bool | None = None
    resource_usb_attributes: bool | None = None
    resource_gpib_intfc_bus_control: bool | None = None
    resource_gpib_intfc_controller_ops: bool | None = None
    extras: Mapping[str, bool] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, bool]) -> "CapabilityFlags":
        values = dict(mapping)
        fields: dict[str, bool | None] = {}
        for key, attr_name in _CAPABILITY_KEY_TO_ATTR.items():
            if key in values:
                fields[attr_name] = bool(values.pop(key))
        return cls(extras={k: bool(v) for k, v in values.items()}, **fields)

    def get(self, capability_key: str, default: bool = False) -> bool:
        attr_name = _CAPABILITY_KEY_TO_ATTR.get(capability_key)
        if attr_name is None:
            return bool(self.extras.get(capability_key, default))
        value = getattr(self, attr_name)
        return default if value is None else bool(value)

    def to_dict(self) -> dict[str, bool]:
        values = dict(self.extras)
        for key, attr_name in _CAPABILITY_KEY_TO_ATTR.items():
            value = getattr(self, attr_name)
            if value is not None:
                values[key] = bool(value)
        return values

    def overlay(self, other: "CapabilityFlags") -> "CapabilityFlags":
        merged = self.to_dict()
        merged.update(other.to_dict())
        return CapabilityFlags.from_mapping(merged)


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
