# -*- coding: utf-8 -*-
"""Instrument-pool abstractions for shared backend contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field

from .profiles import (
    CommandMap,
    InstrumentProfile,
    ProfileMetadata,
    ResourceAddresses,
)

PYVISA_TESTER_TCPIP_RESOURCE_KEYS = (
    "TCPIP::INSTR",
    "TCPIP::HISLIP",
    "TCPIP::SOCKET",
)


@dataclass(frozen=True)
class ResourceCommandFacet(ABC):
    """Command contract for one logical resource class."""

    resource_key: str
    resource_name: str
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, ProfileMetadata):
            raise TypeError("metadata must be a ProfileMetadata instance")

    def prepare_binary_query(self, instrument) -> None:
        """Hook for real instruments needing setup before binary-query use."""
        _ = instrument

    def health_query(self) -> str:
        """Return the health-query command when the instrument exposes one."""
        raise NotImplementedError("Instrument health-query support is unavailable")

    def verify_no_instrument_error(self, instrument) -> None:
        """Hook for instruments exposing an error-query contract."""
        _ = instrument
        raise NotImplementedError("Instrument error-query support is unavailable")

    def binary_configure(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        """Return the staged binary-configuration command."""
        raise NotImplementedError("Staged binary configuration is unavailable")

    def binary_read_query(self) -> str:
        """Return the readback query for staged binary transfers."""
        raise NotImplementedError("Binary readback query is unavailable")

    @abstractmethod
    def binary_query(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        """Return the concrete binary query command."""


@dataclass(frozen=True)
class InstrumentPool(ABC):
    """Map logical resource classes to resource-specific command facets."""

    name: str
    profile_name: str | None = None
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, ProfileMetadata):
            raise TypeError("metadata must be a ProfileMetadata instance")

    @abstractmethod
    def supports_resource(self, resource_key: str) -> bool:
        """Return whether the pool exposes the requested resource key."""

    @abstractmethod
    def for_resource(self, resource_key: str) -> ResourceCommandFacet:
        """Return the command facet for a resource key."""


@dataclass(frozen=True)
class StaticInstrumentPool(InstrumentPool):
    """Pool implementation backed by explicit resource facets."""

    resources: Mapping[str, ResourceCommandFacet] = field(default_factory=dict)

    def supports_resource(self, resource_key: str) -> bool:
        return resource_key in self.resources

    def for_resource(self, resource_key: str) -> ResourceCommandFacet:
        try:
            return self.resources[resource_key]
        except KeyError as exc:
            raise KeyError(f"Pool does not define resource {resource_key}") from exc


@dataclass(frozen=True)
class CommandMapResourceFacet(ResourceCommandFacet):
    """Resource facet backed by shared semantic command mappings."""

    command_map: CommandMap = field(default_factory=CommandMap)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.command_map, CommandMap):
            raise TypeError("command_map must be a CommandMap instance")

    def _command(self, key: str) -> str:
        try:
            return str(self.command_map.require(key))
        except KeyError as exc:
            raise NotImplementedError(f"Command {key} is unavailable") from exc

    def _format_binary_command(
        self,
        template_key: str,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        return self._command(template_key).format(
            datatype=datatype,
            count=count,
            endian=endian,
            header=header,
            termination=termination,
            pattern=pattern,
            start=start,
        )

    def health_query(self) -> str:
        return self._command("health_query")

    def verify_no_instrument_error(self, instrument) -> None:
        response = instrument.query(self._command("error_query")).strip()
        if response.startswith("0") or response.startswith("+0"):
            return
        raise AssertionError(
            f"Instrument reported an error after binary transfer: {response}"
        )

    def binary_query(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        return self._format_binary_command(
            "binary_query_template",
            datatype=datatype,
            count=count,
            endian=endian,
            header=header,
            termination=termination,
            pattern=pattern,
            start=start,
        )

    def binary_configure(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        return self._format_binary_command(
            "binary_configure_template",
            datatype=datatype,
            count=count,
            endian=endian,
            header=header,
            termination=termination,
            pattern=pattern,
            start=start,
        )

    def binary_read_query(self) -> str:
        return self._command("binary_read_query")


@dataclass(frozen=True)
class CommandMapInstrumentPool(InstrumentPool):
    """Default pool implementation backed by a profile and semantic command map."""

    resource_addresses: ResourceAddresses = field(default_factory=ResourceAddresses)
    command_map: CommandMap = field(default_factory=CommandMap)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.resource_addresses, ResourceAddresses):
            raise TypeError("resource_addresses must be a ResourceAddresses instance")
        if not isinstance(self.command_map, CommandMap):
            raise TypeError("command_map must be a CommandMap instance")

    @classmethod
    def from_profile(
        cls,
        profile: InstrumentProfile,
        command_map: CommandMap,
    ) -> "CommandMapInstrumentPool":
        return cls(
            name=profile.name,
            profile_name=profile.name,
            metadata=profile.metadata,
            resource_addresses=profile.resource_addresses,
            command_map=command_map,
        )

    def supports_resource(self, resource_key: str) -> bool:
        return self.resource_addresses.for_resource(resource_key) is not None

    def for_resource(self, resource_key: str) -> ResourceCommandFacet:
        resource_name = self.resource_addresses.for_resource(resource_key)
        if resource_name is None:
            raise KeyError(f"Pool does not define resource {resource_key}")

        return CommandMapResourceFacet(
            resource_key=resource_key,
            resource_name=resource_name,
            metadata=self.metadata,
            command_map=self.command_map,
        )


@dataclass(frozen=True)
class PyvisaTesterTcpipResourceFacet(ResourceCommandFacet):
    """Concrete command facet for pyvisa-tester TCPIP transports."""

    def health_query(self) -> str:
        return "SYST:HEALTH?"

    def verify_no_instrument_error(self, instrument) -> None:
        response = instrument.query("SYST:ERR?").strip()
        if response.startswith("0") or response.startswith("+0"):
            return
        raise AssertionError(
            f"Instrument reported an error after binary transfer: {response}"
        )

    def binary_query(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        return f"DATA:BIN? {datatype},{count},{endian},{header},{termination},{pattern},{start}"

    def binary_configure(
        self,
        *,
        datatype: str,
        count: int,
        endian: str,
        header: str,
        termination: str,
        pattern: str,
        start: int,
    ) -> str:
        return (
            "DATA:BIN:CFG "
            f"{datatype},{count},{endian},{header},{termination},{pattern},{start}"
        )

    def binary_read_query(self) -> str:
        return "DATA:BIN:READ?"


@dataclass(frozen=True)
class PyvisaTesterTcpipInstrumentPool(StaticInstrumentPool):
    """Built-in pool for the shared pyvisa-tester TCPIP resources."""

    @classmethod
    def from_profile(
        cls,
        profile: InstrumentProfile,
    ) -> "PyvisaTesterTcpipInstrumentPool | None":
        if profile.metadata.target != "pyvisa-tester":
            return None

        resources = {
            resource_key: PyvisaTesterTcpipResourceFacet(
                resource_key=resource_key,
                resource_name=resource_name,
                metadata=profile.metadata,
            )
            for resource_key, resource_name in profile.resource_addresses.items()
            if resource_key in PYVISA_TESTER_TCPIP_RESOURCE_KEYS
        }
        if not resources:
            return None

        return cls(
            name="pyvisa-tester-tcpip",
            profile_name=profile.name,
            metadata=profile.metadata,
            resources=resources,
        )


def build_default_instrument_pool(
    profile: InstrumentProfile,
    command_map: CommandMap,
) -> InstrumentPool:
    """Build the default shared instrument pool for a resolved profile."""
    tester_pool = PyvisaTesterTcpipInstrumentPool.from_profile(profile)
    if tester_pool is not None:
        return tester_pool

    return CommandMapInstrumentPool.from_profile(profile, command_map)
