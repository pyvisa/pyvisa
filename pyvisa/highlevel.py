# -*- coding: utf-8 -*-
"""
    pyvisa.highlevel
    ~~~~~~~~~~~~~~~~

    High level Visa library wrapper.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import contextlib
import os
import pkgutil
import warnings
from collections import defaultdict
from importlib import import_module
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ContextManager,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    NewType,
    Optional,
    Set,
    SupportsBytes,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)
from weakref import WeakSet

from typing_extensions import ClassVar, DefaultDict, Literal

from . import constants, errors, logger, rname
from .typing import (
    VISAEventContext,
    VISAHandler,
    VISAJobID,
    VISAMemoryAddress,
    VISASession,
)
from .util import LibraryPath

if TYPE_CHECKING:
    from .resources import Resource

#: Resource extended information
#:
#: Named tuple with information about a resource. Returned by some :class:`ResourceManager` methods.
#:
#: :interface_type: Interface type of the given resource string. :class:`pyvisa.constants.InterfaceType`
#: :interface_board_number: Board number of the interface of the given resource string.
#: :resource_class: Specifies the resource class (for example, "INSTR") of the given resource string.
#: :resource_name: This is the expanded version of the given resource string.
#:                       The format should be similar to the VISA-defined canonical resource name.
#: :alias: Specifies the user-defined alias for the given resource string.
ResourceInfo = NamedTuple(
    "ResourceInfo",
    (
        ("interface_type", constants.InterfaceType),
        ("interface_board_number", int),
        ("resource_class", Optional[str]),
        ("resource_name", Optional[str]),
        ("alias", Optional[str]),
    ),
)

# Used to properly type the __new__ method
T = TypeVar("T", bound="VisaLibraryBase")


class VisaLibraryBase(object):
    """Base for VISA library classes.

    A class derived from `VisaLibraryBase` library provides the low-level communication
    to the underlying devices providing Pythonic wrappers to VISA functions. But not all
    derived class must/will implement all methods. Even if methods are expected to return
    the status code they are expected to raise the appropriate exception when an error
    ocurred since this is more Pythonic.

    The default VisaLibrary class is :class:`pyvisa.ctwrapper.highlevel.IVIVisaLibrary`,
    which implements a ctypes wrapper around the IVI-VISA library.
    Certainly, IVI-VISA can be NI-VISA, Keysight VISA, R&S VISA, tekVISA etc.

    In general, you should not instantiate it directly. The object exposed to the user
    is the :class:`pyvisa.highlevel.ResourceManager`. If needed, you can access the
    VISA library from it::

        >>> import pyvisa
        >>> rm = pyvisa.ResourceManager("/path/to/my/libvisa.so.7")
        >>> lib = rm.visalib
    """

    #: Default ResourceManager instance for this library.
    resource_manager: Optional["ResourceManager"]

    #: Path to the VISA library used by this instance
    library_path: LibraryPath

    #: Maps library path to VisaLibrary object
    _registry: ClassVar[
        Dict[Tuple[Type["VisaLibraryBase"], LibraryPath], "VisaLibraryBase"]
    ] = dict()

    #: Last return value of the library.
    _last_status: constants.StatusCode = constants.StatusCode(0)

    #: Maps session handle to last status.
    _last_status_in_session: Dict[int, constants.StatusCode]

    #: Maps session handle to warnings to ignore.
    _ignore_warning_in_session: Dict[int, set]

    #: Extra inforatoion used for logging errors
    _logging_extra: Dict[str, str]

    #: Contains all installed event handlers.
    #: Its elements are tuples with four elements: The handler itself (a Python
    #: callable), the user handle (in any format making sense to the lower level
    #: implementation, ie as a ctypes object for the ctypes backend) and the
    #: handler again, this time in a format meaningful to the backend (ie as a
    #: ctypes object created with CFUNCTYPE for the ctypes backend) and
    #: the event type.
    handlers: DefaultDict[VISASession, List[Tuple[VISAHandler, Any, Any, Any]]]

    #: Set error codes on which to issue a warning.
    # XXX improve
    issue_warning_on: Set[constants.StatusCode]

    def __new__(
        cls: Type[T], library_path: Union[str, LibraryPath] = ""
    ) -> "VisaLibraryBase":
        if library_path == "":
            errs = []
            for path in cls.get_library_paths():
                try:
                    return cls(path)
                except OSError as e:
                    logger.debug("Could not open VISA library %s: %s", path, str(e))
                    errs.append(str(e))
                except Exception as e:
                    errs.append(str(e))
            else:
                raise OSError("Could not open VISA library:\n" + "\n".join(errs))

        if not isinstance(library_path, LibraryPath):
            lib_path = LibraryPath(library_path, "user specified")

        if (cls, lib_path) in cls._registry:
            return cls._registry[(cls, lib_path)]

        obj = super(VisaLibraryBase, cls).__new__(cls)

        obj.library_path = lib_path

        obj._logging_extra = {"library_path": obj.lib_path}

        obj._init()

        # Create instance specific registries.
        #: Error codes on which to issue a warning.
        obj.issue_warning_on = set(errors.default_warnings)
        obj._last_status_in_session = dict()
        obj._ignore_warning_in_session = defaultdict(set)
        obj.handlers = defaultdict(list)
        obj.resource_manager = None

        logger.debug("Created library wrapper for %s", lib_path)

        cls._registry[(cls, lib_path)] = obj

        return obj

    @staticmethod
    def get_library_paths() -> Iterable[LibraryPath]:
        """Override this method to return an iterable of possible library_paths
        to try in case that no argument is given.
        """
        return ()

    @staticmethod
    def get_debug_info() -> Union[Iterable[str], Dict[str, Union[str, Dict[str, Any]]]]:
        """Override this method to return an iterable of lines with the backend debug details.

        """
        return ["Does not provide debug info"]

    def _init(self) -> None:
        """Override this method to customize VisaLibrary initialization.

        """
        pass

    def __str__(self) -> str:
        return "Visa Library at %s" % self.library_path

    def __repr__(self) -> str:
        return "<VisaLibrary(%r)>" % self.library_path

    @property
    def last_status(self) -> constants.StatusCode:
        """Last return value of the library.

        """
        return self._last_status

    def get_last_status_in_session(self, session: VISASession) -> constants.StatusCode:
        """Last status in session.

        Helper function to be called by resources properties.
        """
        try:
            return self._last_status_in_session[session]
        except KeyError:
            raise errors.Error(
                "The session %r does not seem to be valid as it does not have any last status"
                % session
            )

    @contextlib.contextmanager
    def ignore_warning(
        self, session: VISASession, *warnings_constants: constants.StatusCode
    ) -> Iterator:
        """A session dependent context for ignoring warnings

        :param session: Unique logical identifier to a session.
        :param warnings_constants: constants identifying the warnings to ignore.
        """
        self._ignore_warning_in_session[session].update(warnings_constants)
        yield
        self._ignore_warning_in_session[session].difference_update(warnings_constants)

    def install_visa_handler(
        self,
        session: VISASession,
        event_type: constants.EventType,
        handler: VISAHandler,
        user_handle: Any = None,
    ) -> Any:
        """Installs handlers for event callbacks.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: user handle (a ctypes object)
        """
        try:
            new_handler = self.install_handler(
                session, event_type, handler, user_handle
            )
        except TypeError as e:
            raise errors.VisaTypeError(str(e))

        self.handlers[session].append(new_handler[:-1] + (event_type,))
        return new_handler[1]

    def uninstall_visa_handler(
        self,
        session: VISASession,
        event_type: constants.EventType,
        handler: VISAHandler,
        user_handle: Any = None,
    ) -> None:
        """Uninstalls handlers for events.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: The user handle (ctypes object or None) returned by install_visa_handler.
        """
        for ndx, element in enumerate(self.handlers[session]):
            # use == rather than is to allow bound methods as handlers
            reveal_type(element)
            if (
                element[0] == handler
                and element[1] is user_handle
                and element[3] == event_type
            ):
                del self.handlers[session][ndx]
                break
        else:
            raise errors.UnknownHandler(event_type, handler, user_handle)
        self.uninstall_handler(session, event_type, element[2], user_handle)

    def __uninstall_all_handlers_helper(self, session: VISASession) -> None:
        for element in self.handlers[session]:
            self.uninstall_handler(session, element[3], element[2], element[1])
        del self.handlers[session]

    def uninstall_all_visa_handlers(self, session: VISASession) -> None:
        """Uninstalls all previously installed handlers for a particular session.

        :param session: Unique logical identifier to a session. If None, operates on all sessions.
        """

        if session is not None:
            self.__uninstall_all_handlers_helper(session)
        else:
            for session in list(self.handlers):
                self.__uninstall_all_handlers_helper(session)

    def read_memory(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
        extended: bool = False,
    ) -> Tuple[int, constants.StatusCode]:
        """Reads in an 8-bit, 16-bit, 32-bit, or 64-bit value from the specified memory space and offset.

        Corresponds to viIn* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"in_{w}")(session, space, offset, extended)

    def write_memory(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        data: int,
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 8-bit, 16-bit, 32-bit, 64-bit value to the specified memory space and offset.

        Corresponds to viOut* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param width: Number of bits to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"out_{w}")(session, space, offset, data, extended)

    def move_in(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
        extended: bool = False,
    ) -> Tuple[List[int], constants.StatusCode]:
        """Moves a block of data to local memory from the specified address space and offset.

        Corresponds to viMoveIn* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"move_in_{w}")(session, space, offset, length, extended)

    def move_out(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves a block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param width: Number of bits to read per element.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"move_out_{w}")(
            session, space, offset, length, data, extended
        )

    def peek(
        self,
        session: VISASession,
        address: VISAMemoryAddress,
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
    ) -> Tuple[int, constants.StatusCode]:
        """Read an 8, 16, 32, or 64-bit value from the specified address.

        Corresponds to viPeek* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param width: Number of bits to read.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"peek_{w}")(session, address)

    def poke(
        self,
        session: VISASession,
        address: VISAMemoryAddress,
        width: Union[Literal[8, 16, 32, 64], constants.DataWidth],
        data: int,
    ) -> constants.StatusCode:
        """Writes an 8, 16, 32, or 64-bit value from the specified address.

        Corresponds to viPoke* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param width: Number of bits to read.
        :param data: Data to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        w = width * 8 if isinstance(width, constants.DataWidth) else width
        if w not in (8, 16, 32, 64):
            raise ValueError(
                "%s is not a valid size. Valid values are 8, 16, 32 or 64 "
                "or one member of constants.DataWidth" % width
            )
        return getattr(self, f"poke_{w}")(session, address, data)

    # Methods that VISA Library implementations must implement

    def assert_interrupt_signal(
        self,
        session: VISASession,
        mode: constants.AssertSignalInterrupt,
        status_id: int,
    ) -> constants.StatusCode:
        """Asserts the specified interrupt or signal.

        Corresponds to viAssertIntrSignal function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: How to assert the interrupt. (Constants.ASSERT*)
        :param status_id: This is the status value to be presented during an interrupt acknowledge cycle.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def assert_trigger(
        self, session: VISASession, protocol: constants.TriggerProtocol
    ) -> constants.StatusCode:
        """Asserts software or hardware trigger.

        Corresponds to viAssertTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param protocol: Trigger protocol to use during assertion. (Constants.PROT*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def assert_utility_signal(
        self, session: VISASession, line: constants.UtilityBusSignal
    ) -> constants.StatusCode:
        """Asserts or deasserts the specified utility bus signal.

        Corresponds to viAssertUtilSignal function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param line: specifies the utility bus signal to assert. (Constants.VI_UTIL_ASSERT*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def buffer_read(
        self, session: VISASession, count: int
    ) -> Tuple[bytes, constants.StatusCode]:
        """Reads data from device or interface through the use of a formatted I/O read buffer.

        Corresponds to viBufRead function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: data read, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def buffer_write(
        self, session: VISASession, data: bytes
    ) -> Tuple[int, constants.StatusCode]:
        """Writes data to a formatted I/O write buffer synchronously.

        Corresponds to viBufWrite function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :type data: bytes
        :return: number of written bytes, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def clear(self, session: VISASession) -> constants.StatusCode:
        """Clears a device.

        Corresponds to viClear function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def close(self, session: VISASession) -> constants.StatusCode:
        """Closes the specified session: VISASession, event, or find list.

        Corresponds to viClose function of the VISA library.

        :param session: Unique logical identifier to a session, event, or find list.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def disable_event(
        self,
        session: VISASession,
        event_type: constants.EventType,
        mechanism: constants.EventMechanism,
    ) -> constants.StatusCode:
        """Disables notification of the specified event type(s) via the specified mechanism(s).

        Corresponds to viDisableEvent function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be disabled.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def discard_events(
        self,
        session: VISASession,
        event_type: constants.EventType,
        mechanism: constants.EventMechanism,
    ) -> constants.StatusCode:
        """Discards event occurrences for specified event types and mechanisms in a session.

        Corresponds to viDiscardEvents function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be discarded.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR, .VI_ALL_MECH)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def enable_event(
        self,
        session: VISASession,
        event_type: constants.EventType,
        mechanism: constants.EventMechanism,
        context: None = None,
    ):
        """Enable event occurrences for specified event types and mechanisms in a session.

        Corresponds to viEnableEvent function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param mechanism: Specifies event handling mechanisms to be enabled.
                          (Constants.VI_QUEUE, .VI_HNDLR, .VI_SUSPEND_HNDLR)
        :param context:
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def flush(
        self, session: VISASession, mask: constants.BufferOperation
    ) -> constants.StatusCode:
        """Manually flushes the specified buffers associated with formatted
        I/O operations and/or serial communication.

        Corresponds to viFlush function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mask: Specifies the action to be taken with flushing the buffer.
            The following values (defined in the constants module can be
            combined using the | operator. However multiple operations on a
            single buffer cannot be combined.

        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`

        """
        raise NotImplementedError

    def get_attribute(
        self, session: VISASession, attribute: constants.Attribute
    ) -> Tuple[Any, constants.StatusCode]:
        """Retrieves the state of an attribute.

        Corresponds to viGetAttribute function of the VISA library.

        :param session: Unique logical identifier to a session, event, or find list.
        :param attribute: Resource attribute for which the state query is made (see Attributes.*)
        :return: The state of the queried attribute for a specified resource, return value of the library call.
        :rtype: unicode (Py2) or str (Py3), list or other type, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_command(
        self, session: VISASession, data: bytes
    ) -> Tuple[int, constants.StatusCode]:
        """Write GPIB command bytes on the bus.

        Corresponds to viGpibCommand function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data tor write.
        :type data: bytes
        :return: Number of written bytes, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_control_atn(
        self, session: VISASession, mode: constants.ATNLineOperation
    ) -> constants.StatusCode:
        """Specifies the state of the ATN line and the local active controller state.

        Corresponds to viGpibControlATN function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies the state of the ATN line and optionally the local active controller state.
                     (Constants.VI_GPIB_ATN*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_control_ren(
        self, session: VISASession, mode: constants.RENLineOperation
    ) -> constants.StatusCode:
        """Controls the state of the GPIB Remote Enable (REN) interface line, and optionally the remote/local
        state of the device.

        Corresponds to viGpibControlREN function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies the state of the REN line and optionally the device remote/local state.
                     (Constants.VI_GPIB_REN*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_pass_control(
        self, session: VISASession, primary_address: int, secondary_address: int
    ) -> constants.StatusCode:
        """Tell the GPIB device at the specified address to become controller in charge (CIC).

        Corresponds to viGpibPassControl function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param primary_address: Primary address of the GPIB device to which you want to pass control.
        :param secondary_address: Secondary address of the targeted GPIB device.
                                  If the targeted device does not have a secondary address,
                                  this parameter should contain the value Constants.VI_NO_SEC_ADDR.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def gpib_send_ifc(self, session: VISASession) -> constants.StatusCode:
        """Pulse the interface clear line (IFC) for at least 100 microseconds.

        Corresponds to viGpibSendIFC function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_8(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        extended: bool = False,
    ) -> Tuple[int, constants.StatusCode]:
        """Reads in an 8-bit value from the specified memory space and offset.

        Corresponds to viIn8* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_16(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        extended: bool = False,
    ) -> Tuple[int, constants.StatusCode]:
        """Reads in an 16-bit value from the specified memory space and offset.

        Corresponds to viIn16* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_32(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        extended: bool = False,
    ) -> Tuple[int, constants.StatusCode]:
        """Reads in an 32-bit value from the specified memory space and offset.

        Corresponds to viIn32* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def in_64(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        extended: bool = False,
    ) -> Tuple[int, constants.StatusCode]:
        """Reads in an 64-bit value from the specified memory space and offset.

        Corresponds to viIn64* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from memory, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def install_handler(
        self,
        session: VISASession,
        event_type: constants.EventType,
        handler: VISAHandler,
        user_handle: Any,
    ) -> Tuple[VISAHandler, Any, Any, constants.StatusCode]:
        """Installs handlers for event callbacks.

        Corresponds to viInstallHandler function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be installed by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely for an event type.
        :returns: a handler descriptor which consists of three elements:
                 - handler (a python callable)
                 - user handle (a ctypes object)
                 - ctypes handler (ctypes object wrapping handler)
                 and return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def list_resources(
        self, session: VISASession, query: str = "?*::INSTR"
    ) -> Tuple[str, ...]:
        """Returns a tuple of all connected devices matching query.

        :param query: regular expression used to match devices.
        """
        raise NotImplementedError

    def lock(
        self,
        session: VISASession,
        lock_type: constants.Lock,
        timeout: int,
        requested_key: Optional[str] = None,
    ) -> Tuple[str, constants.StatusCode]:
        """Establishes an access mode to the specified resources.

        Corresponds to viLock function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param lock_type: Specifies the type of lock requested, either Constants.EXCLUSIVE_LOCK or Constants.SHARED_LOCK.
        :param timeout: Absolute time period (in milliseconds) that a resource waits to get unlocked by the
                        locking session before returning an error.
        :param requested_key: This parameter is not used and should be set to VI_NULL when lockType is VI_EXCLUSIVE_LOCK.
        :return: access_key that can then be passed to other sessions to share the lock, return value of the library call.
        :rtype: str, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def map_address(
        self,
        session: VISASession,
        map_space: constants.AddressSpace,
        map_base: int,
        map_size: int,
        access: bool = False,
        suggested: int = None,
    ) -> Tuple[int, constants.StatusCode]:
        """Maps the specified memory space into the process's address space.

        Corresponds to viMapAddress function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param map_space: Specifies the address space to map. (Constants.*SPACE*)
        :param map_base: Offset (in bytes) of the memory to be mapped.
        :param map_size: Amount of memory to map (in bytes).
        :param access:
        :param suggested: If not Constants.VI_NULL (0), the operating system attempts to map the memory to the address
                          specified in suggested. There is no guarantee, however, that the memory will be mapped to
                          that address. This operation may map the memory into an address region different from
                          suggested.

        :return: address in your process space where the memory was mapped, return value of the library call.
        :rtype: address, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def map_trigger(
        self,
        session: VISASession,
        trigger_source: constants.InputTriggerLine,
        trigger_destination: constants.OutputTriggerLine,
        mode: None = None,
    ) -> constants.StatusCode:
        """Map the specified trigger source line to the specified destination line.

        Corresponds to viMapTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param trigger_source: Source line from which to map. (Constants.VI_TRIG*)
        :param trigger_destination: Destination line to which to map. (Constants.VI_TRIG*)
        :param mode: Always None for this version of the VISA specification.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def memory_allocation(
        self, session: VISASession, size: int, extended: bool = False
    ) -> Tuple[int, constants.StatusCode]:
        """Allocates memory from a resource's memory region.

        Corresponds to viMemAlloc* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param size: Specifies the size of the allocation.
        :param extended: Use 64 bits offset independent of the platform.
        :return: offset of the allocated memory, return value of the library call.
        :rtype: offset, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def memory_free(
        self, session: VISASession, offset: int, extended: bool = False
    ) -> constants.StatusCode:
        """Frees memory previously allocated using the memory_allocation() operation.

        Corresponds to viMemFree* function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param offset: Offset of the memory to free.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move(
        self,
        session: VISASession,
        source_space: constants.AddressSpace,
        source_offset: int,
        source_width: constants.DataWidth,
        destination_space: constants.AddressSpace,
        destination_offset: int,
        destination_width: constants.DataWidth,
        length: int,
    ) -> constants.StatusCode:
        """Moves a block of data.

        Corresponds to viMove function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param source_space: Specifies the address space of the source.
        :param source_offset: Offset of the starting address or register from which to read.
        :param source_width: Specifies the data width of the source.
        :param destination_space: Specifies the address space of the destination.
        :param destination_offset: Offset of the starting address or register to which to write.
        :param destination_width: Specifies the data width of the destination.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_asynchronously(
        self,
        session: VISASession,
        source_space: constants.AddressSpace,
        source_offset: int,
        source_width: constants.DataWidth,
        destination_space: constants.AddressSpace,
        destination_offset: int,
        destination_width: constants.DataWidth,
        length: int,
    ) -> Tuple[VISAJobID, constants.StatusCode]:
        """Moves a block of data asynchronously.

        Corresponds to viMoveAsync function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param source_space: Specifies the address space of the source.
        :param source_offset: Offset of the starting address or register from which to read.
        :param source_width: Specifies the data width of the source.
        :param destination_space: Specifies the address space of the destination.
        :param destination_offset: Offset of the starting address or register to which to write.
        :param destination_width: Specifies the data width of the destination.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :return: Job identifier of this asynchronous move operation, return value of the library call.
        :rtype: jobid, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_8(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        extended: bool = False,
    ) -> Tuple[List[int], constants.StatusCode]:
        """Moves an 8-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn8* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_16(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        extended: bool = False,
    ) -> Tuple[List[int], constants.StatusCode]:
        """Moves an 16-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn16* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_32(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        extended: bool = False,
    ) -> Tuple[List]:
        """Moves an 32-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn32* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_in_64(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        extended: bool = False,
    ) -> Tuple[List[int], constants.StatusCode]:
        """Moves an 64-bit block of data from the specified address space and offset to local memory.

        Corresponds to viMoveIn64* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param extended: Use 64 bits offset independent of the platform.
        :return: Data read from the bus, return value of the library call.
        :rtype: list, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_out_8(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves an 8-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut8* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`

        Corresponds to viMoveOut8 function of the VISA library.
        """
        raise NotImplementedError

    def move_out_16(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves an 16-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut16* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_out_32(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves an 32-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut32* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def move_out_64(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        length: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Moves an 64-bit block of data from local memory to the specified address space and offset.

        Corresponds to viMoveOut64* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param length: Number of elements to transfer, where the data width of the elements to transfer
                       is identical to the source data width.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def open(
        self,
        session: VISASession,
        resource_name: str,
        access_mode: constants.AccessModes = constants.AccessModes.no_lock,
        open_timeout: int = constants.VI_TMO_IMMEDIATE,
    ) -> Tuple[VISASession, constants.StatusCode]:
        """Opens a session to the specified resource.

        Corresponds to viOpen function of the VISA library.

        :param session: Resource Manager session (should always be a session returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int
        :return: Unique logical identifier reference to a session, return value of the library call.
        :rtype: session, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def open_default_resource_manager(self) -> Tuple[VISASession, constants.StatusCode]:
        """This function returns a session to the Default Resource Manager resource.

        Corresponds to viOpenDefaultRM function of the VISA library.

        :return: Unique logical identifier to a Default Resource Manager session, return value of the library call.
        :rtype: session, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_8(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 8-bit value from the specified memory space and offset.

        Corresponds to viOut8* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_16(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 16-bit value from the specified memory space and offset.

        Corresponds to viOut16* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_32(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 32-bit value from the specified memory space and offset.

        Corresponds to viOut32* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def out_64(
        self,
        session: VISASession,
        space: constants.AddressSpace,
        offset: int,
        data: Iterable[int],
        extended: bool = False,
    ) -> constants.StatusCode:
        """Write in an 64-bit value from the specified memory space and offset.

        Corresponds to viOut64* functions of the VISA library.

        :param session: Unique logical identifier to a session.
        :param space: Specifies the address space. (Constants.*SPACE*)
        :param offset: Offset (in bytes) of the address or register from which to read.
        :param data: Data to write to bus.
        :param extended: Use 64 bits offset independent of the platform.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def parse_resource(
        self, session: VISASession, resource_name: str
    ) -> Tuple[ResourceInfo, constants.StatusCode]:
        """Parse a resource string to get the interface information.

        Corresponds to viParseRsrc function of the VISA library.

        :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                        returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :return: Resource information with interface type and board number, return value of the library call.
        :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
        """
        ri, status = self.parse_resource_extended(session, resource_name)
        if ri:
            return (
                ResourceInfo(
                    ri.interface_type, ri.interface_board_number, None, None, None
                ),
                constants.StatusCode.success,
            )
        else:
            return ri, status

    def parse_resource_extended(
        self, session: VISASession, resource_name: str
    ) -> Tuple[ResourceInfo, constants.StatusCode]:
        """Parse a resource string to get extended interface information.

        Corresponds to viParseRsrcEx function of the VISA library.

        :param session: Resource Manager session (should always be the Default Resource Manager for VISA
                        returned from open_default_resource_manager()).
        :param resource_name: Unique symbolic name of a resource.
        :return: Resource information, return value of the library call.
        :rtype: :class:`pyvisa.highlevel.ResourceInfo`, :class:`pyvisa.constants.StatusCode`
        """
        try:
            parsed = rname.parse_resource_name(resource_name)

            return (
                ResourceInfo(
                    parsed.interface_type_const,
                    int(parsed.board),  # match IVI-VISA
                    parsed.resource_class,
                    str(parsed),
                    None,
                ),
                constants.StatusCode.success,
            )
        except ValueError:
            return (
                ResourceInfo(constants.InterfaceType.unknown, 0, None, None, None),
                constants.StatusCode.error_invalid_resource_name,
            )

    def peek_8(
        self, session: VISASession, address: VISAMemoryAddress
    ) -> Tuple[int, constants.StatusCode]:
        """Read an 8-bit value from the specified address.

        Corresponds to viPeek8 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_16(
        self, session: VISASession, address: VISAMemoryAddress
    ) -> Tuple[int, constants.StatusCode]:
        """Read an 16-bit value from the specified address.

        Corresponds to viPeek16 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_32(
        self, session: VISASession, address: VISAMemoryAddress
    ) -> Tuple[int, constants.StatusCode]:
        """Read an 32-bit value from the specified address.

        Corresponds to viPeek32 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def peek_64(
        self, session: VISASession, address: VISAMemoryAddress
    ) -> Tuple[int, constants.StatusCode]:
        """Read an 64-bit value from the specified address.

        Corresponds to viPeek64 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :return: Data read from bus, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_8(
        self, session: VISASession, address: VISAMemoryAddress, data: int
    ) -> constants.StatusCode:
        """Write an 8-bit value from the specified address.

        Corresponds to viPoke8 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: Data read from bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_16(
        self, session: VISASession, address: VISAMemoryAddress, data: int
    ) -> constants.StatusCode:
        """Write an 16-bit value from the specified address.

        Corresponds to viPoke16 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_32(
        self, session: VISASession, address: VISAMemoryAddress, data: int
    ) -> constants.StatusCode:
        """Write an 32-bit value from the specified address.

        Corresponds to viPoke32 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def poke_64(
        self, session: VISASession, address: VISAMemoryAddress, data: int
    ) -> constants.StatusCode:
        """Write an 64-bit value from the specified address.

        Corresponds to viPoke64 function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param address: Source address to read the value.
        :param data: value to be written to the bus.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read(
        self, session: VISASession, count: int
    ) -> Tuple[bytes, constants.StatusCode]:
        """Reads data from device or interface synchronously.

        Corresponds to viRead function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: data read, return value of the library call.
        :rtype: bytes, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_asynchronously(
        self, session: VISASession, count: int
    ) -> Tuple[SupportsBytes, VISAJobID, constants.StatusCode]:
        """Reads data from device or interface asynchronously.

        Corresponds to viReadAsync function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param count: Number of bytes to be read.
        :return: result, jobid, return value of the library call.
        :rtype: ctypes buffer, jobid, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_stb(self, session: VISASession) -> Tuple[int, constants.StatusCode]:
        """Reads a status byte of the service request.

        Corresponds to viReadSTB function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: Service request status byte, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def read_to_file(
        self, session: VISASession, filename: str, count: int
    ) -> Tuple[int, constants.StatusCode]:
        """Read data synchronously, and store the transferred data in a file.

        Corresponds to viReadToFile function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param filename: Name of file to which data will be written.
        :param count: Number of bytes to be read.
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def set_attribute(
        self, session: VISASession, attribute: constants.Attribute, attribute_state: Any
    ) -> constants.StatusCode:
        """Sets the state of an attribute.

        Corresponds to viSetAttribute function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param attribute: Attribute for which the state is to be modified. (Attributes.*)
        :param attribute_state: The state of the attribute to be set for the specified object.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def set_buffer(
        self, session: VISASession, mask: constants.BufferType, size: int
    ) -> constants.StatusCode:
        """Sets the size for the formatted I/O and/or low-level I/O communication buffer(s).

        Corresponds to viSetBuf function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mask: Specifies the type of buffer. (Constants.VI_READ_BUF, .VI_WRITE_BUF, .VI_IO_IN_BUF, .VI_IO_OUT_BUF)
        :param size: The size to be set for the specified buffer(s).
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def status_description(
        self, session: VISASession, status: constants.StatusCode
    ) -> Tuple[str, constants.StatusCode]:
        """Returns a user-readable description of the status code passed to the operation.

        Corresponds to viStatusDesc function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param status: Status code to interpret.
        :return: - The user-readable string interpretation of the status code passed to the operation,
                 - return value of the library call.
        :rtype: - unicode (Py2) or str (Py3)
                - :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def terminate(
        self, session: VISASession, degree: None, job_id: VISAJobID
    ) -> constants.StatusCode:
        """Requests a VISA session to terminate normal execution of an operation.

        Corresponds to viTerminate function of the VISA library.

        If a user passes VI_NULL as the jobId value to viTerminate(), a VISA implementation should abort any calls in the current process executing on the specified vi. Any call that is terminated this way should return VI_ERROR_ABORT.

        :param session: Unique logical identifier to a session.
        :param degree: Constants.NULL
        :param job_id: Specifies an operation identifier.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def uninstall_handler(
        self,
        session: VISASession,
        event_type: constants.EventType,
        handler: Any,
        user_handle: Any = None,
    ) -> constants.StatusCode:
        """Uninstalls handlers for events.

        Corresponds to viUninstallHandler function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param event_type: Logical event identifier.
        :param handler: Interpreted as a valid reference to a handler to be uninstalled by a client application.
        :param user_handle: A value specified by an application that can be used for identifying handlers
                            uniquely in a session for an event.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unlock(self, session: VISASession) -> constants.StatusCode:
        """Relinquishes a lock for the specified resource.

        Corresponds to viUnlock function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unmap_address(self, session: VISASession) -> constants.StatusCode:
        """Unmaps memory space previously mapped by map_address().

        Corresponds to viUnmapAddress function of the VISA library.

        :param session: Unique logical identifier to a session.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def unmap_trigger(
        self,
        session: VISASession,
        trigger_source: constants.InputTriggerLine,
        trigger_destination: constants.OutputTriggerLine,
    ) -> constants.StatusCode:
        """Undo a previous map from the specified trigger source line to the specified destination line.

        Corresponds to viUnmapTrigger function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param trigger_source: Source line used in previous map. (Constants.VI_TRIG*)
        :param trigger_destination: Destination line used in previous map. (Constants.VI_TRIG*)
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def usb_control_in(
        self,
        session: VISASession,
        request_type_bitmap_field: int,
        request_id: int,
        request_value: int,
        index: int,
        length: int = 0,
    ) -> Tuple[bytes, constants.StatusCode]:
        """Performs a USB control pipe transfer from the device.

        Corresponds to viUsbControlIn function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param length: wLength parameter of the setup stage of a USB control transfer.
                       This value also specifies the size of the data buffer to receive the data from the
                       optional data stage of the control transfer.
        :return: - The data buffer that receives the data from the optional data stage of the control transfer
                 - return value of the library call.
        :rtype: - bytes
                - :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def usb_control_out(
        self,
        session: VISASession,
        request_type_bitmap_field: int,
        request_id: int,
        request_value: int,
        index: int,
        data: str = "",
    ) -> constants.StatusCode:
        """Performs a USB control pipe transfer to the device.

        Corresponds to viUsbControlOut function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param request_type_bitmap_field: bmRequestType parameter of the setup stage of a USB control transfer.
        :param request_id: bRequest parameter of the setup stage of a USB control transfer.
        :param request_value: wValue parameter of the setup stage of a USB control transfer.
        :param index: wIndex parameter of the setup stage of a USB control transfer.
                      This is usually the index of the interface or endpoint.
        :param data: The data buffer that sends the data in the optional data stage of the control transfer.
        :return: return value of the library call.
        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def vxi_command_query(
        self, session: VISASession, mode: constants.VXICommands, command: int
    ) -> Tuple[int, constants.StatusCode]:
        """Sends the device a miscellaneous command or query and/or retrieves the response to a previous query.

        Corresponds to viVxiCommandQuery function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param mode: Specifies whether to issue a command and/or retrieve a response. (Constants.VI_VXI_CMD*, .VI_VXI_RESP*)
        :param command: The miscellaneous command to send.
        :return: The response retrieved from the device, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def wait_on_event(
        self, session: VISASession, in_event_type: constants.EventType, timeout: int
    ) -> Tuple[constants.EventType, VISAEventContext, constants.StatusCode]:
        """Waits for an occurrence of the specified event for a given session.

        Corresponds to viWaitOnEvent function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param in_event_type: Logical identifier of the event(s) to wait for.
        :param timeout: Absolute time period in time units that the resource shall wait for a specified event to
                        occur before returning the time elapsed error. The time unit is in milliseconds.
        :return: - Logical identifier of the event actually received
                 - A handle specifying the unique occurrence of an event
                 - return value of the library call.
        :rtype: - eventtype
                - event
                - :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def write(
        self, session: VISASession, data: bytes
    ) -> Tuple[int, constants.StatusCode]:
        """Writes data to device or interface synchronously.

        Corresponds to viWrite function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :type data: str
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def write_asynchronously(
        self, session: VISASession, data: bytes
    ) -> Tuple[VISAJobID, constants.StatusCode]:
        """Writes data to device or interface asynchronously.

        Corresponds to viWriteAsync function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param data: data to be written.
        :return: Job ID of this asynchronous write operation, return value of the library call.
        :rtype: jobid, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError

    def write_from_file(
        self, session: VISASession, filename: str, count: int
    ) -> Tuple[int, constants.StatusCode]:
        """Take data from a file and write it out synchronously.

        Corresponds to viWriteFromFile function of the VISA library.

        :param session: Unique logical identifier to a session.
        :param filename: Name of file from which data will be read.
        :param count: Number of bytes to be written.
        :return: Number of bytes actually transferred, return value of the library call.
        :rtype: int, :class:`pyvisa.constants.StatusCode`
        """
        raise NotImplementedError


def list_backends() -> List[str]:
    """Return installed backends.

    Backends are installed python packages named pyvisa-<something> where <something>
    is the name of the backend.

    :rtype: list
    """
    return ["ivi"] + [
        name
        for (loader, name, ispkg) in pkgutil.iter_modules()
        if name.startswith("pyvisa-") and not name.endswith("-script")
    ]


#: Maps backend name to VisaLibraryBase derived class
_WRAPPERS: Dict[str, Type[VisaLibraryBase]] = {}


class PyVISAModule(ModuleType):

    WRAPPER_CLASS: Type[VisaLibraryBase]


def get_wrapper_class(backend_name: str) -> Type[VisaLibraryBase]:
    """Return the WRAPPER_CLASS for a given backend.

    backend_name == 'ni' is used for backwards compatibility
    and will be removed in 1.12.

    :rtype: pyvisa.highlevel.VisaLibraryBase
    """
    try:
        return _WRAPPERS[backend_name]
    except KeyError:
        if backend_name == "ivi" or backend_name == "ni":
            from .ctwrapper import IVIVisaLibrary

            _WRAPPERS["ivi"] = IVIVisaLibrary
            if backend_name == "ni":
                warnings.warn(
                    "@ni backend name is deprecated and will be "
                    "removed in 1.12. Use @ivi instead. "
                    "Check the documentation for details",
                    FutureWarning,
                )
            return IVIVisaLibrary

    try:
        pkg: PyVISAModule = cast(PyVISAModule, import_module("pyvisa-" + backend_name))
        _WRAPPERS[backend_name] = cls = pkg.WRAPPER_CLASS
        return cls
    except ImportError:
        raise ValueError("Wrapper not found: No package named pyvisa-%s" % backend_name)


def _get_default_wrapper() -> str:
    """Return an available default VISA wrapper as a string ('ivi' or 'py').

    Use IVI if the binary is found, else try to use pyvisa-py.

    'ni' VISA wrapper is NOT used since version > 1.10.0
    and will be removed in 1.12

    If neither can be found, raise a ValueError.
    """

    from .ctwrapper import IVIVisaLibrary

    ivi_binary_found = bool(IVIVisaLibrary.get_library_paths())
    if ivi_binary_found:
        logger.debug("The IVI implementation available")
        return "ivi"
    else:
        logger.debug("Did not find IVI binary")

    try:
        get_wrapper_class("py")  # check for pyvisa-py availability
        logger.debug("pyvisa-py is available.")
        return "py"
    except ValueError:
        logger.debug("Did not find pyvisa-py package")
    raise ValueError(
        "Could not locate a VISA implementation. Install either the IVI binary or pyvisa-py."
    )


def open_visa_library(specification: str) -> VisaLibraryBase:
    """Helper function to create a VISA library wrapper.

    In general, you should not use the function directly. The VISA library
    wrapper will be created automatically when you create a ResourceManager object.
    """

    if not specification:
        logger.debug("No visa library specified, trying to find alternatives.")
        try:
            specification = os.environ["PYVISA_LIBRARY"]
        except KeyError:
            logger.debug("Environment variable PYVISA_LIBRARY is unset.")

    wrapper: Optional[str]
    try:
        argument, wrapper = specification.split("@")
    except ValueError:
        argument = specification
        wrapper = None  # Flag that we need a fallback, but avoid nested exceptions
    if wrapper is None:
        if argument:  # some filename given
            wrapper = "ivi"
        else:
            wrapper = _get_default_wrapper()

    cls = get_wrapper_class(wrapper)

    try:
        return cls(argument)
    except Exception as e:
        logger.debug("Could not open VISA wrapper %s: %s\n%s", cls, str(argument), e)
        raise


class ResourceManager(object):
    """VISA Resource Manager

    :param visa_library: VisaLibrary Instance, path of the VISA library or VisaLibrary spec string.
                         (if not given, the default for the platform will be used).
    """

    #: Maps (Interface Type, Resource Class) to Python class encapsulating that resource.
    _resource_classes: Dict[
        Tuple[constants.InterfaceType, str], Type[Resource]
    ] = dict()

    #: Session handler for the resource manager.
    _session: Optional[VISASession] = None

    #: Reference to the VISA library used by the ResourceManager
    visalib: VisaLibraryBase

    #: Resources created by this manager to allow closing them when the manager is closed
    _created_resources: WeakSet

    @classmethod
    def register_resource_class(
        cls,
        interface_type: constants.InterfaceType,
        resource_class: str,
        python_class: Type[Resource],
    ) -> None:
        if (interface_type, resource_class) in cls._resource_classes:
            logger.warning(
                "%s is already registered in the ResourceManager. "
                "Overwriting with %s" % ((interface_type, resource_class), python_class)
            )
        cls._resource_classes[(interface_type, resource_class)] = python_class

    def __new__(
        cls: Type["ResourceManager"], visa_library: Union[str, VisaLibraryBase] = ""
    ) -> "ResourceManager":
        if not isinstance(visa_library, VisaLibraryBase):
            visa_library = open_visa_library(visa_library)

        if visa_library.resource_manager is not None:
            obj = visa_library.resource_manager
            logger.debug("Reusing ResourceManager with session %s", obj.session)
            return obj

        obj = super(ResourceManager, cls).__new__(cls)

        obj.session, err = visa_library.open_default_resource_manager()

        obj.visalib = visa_library
        obj.visalib.resource_manager = obj
        obj._created_resources = WeakSet()

        logger.debug("Created ResourceManager with session %s", obj.session)
        return obj

    @property
    def session(self) -> VISASession:
        """Resource Manager session handle.

        :raises: :class:`pyvisa.errors.InvalidSession` if session is closed.
        """
        if self._session is None:
            raise errors.InvalidSession()
        return self._session

    @session.setter
    def session(self, value: Optional[VISASession]) -> None:
        self._session = value

    def __str__(self) -> str:
        return "Resource Manager of %s" % self.visalib

    def __repr__(self) -> str:
        return "<ResourceManager(%r)>" % self.visalib

    def __del__(self) -> None:
        if self._session is not None:
            self.close()

    def ignore_warning(
        self, *warnings_constants: constants.StatusCode
    ) -> ContextManager:
        """Ignoring warnings context manager for the current resource.

        :param warnings_constants: constants identifying the warnings to ignore.
        """
        return self.visalib.ignore_warning(self.session, *warnings_constants)

    @property
    def last_status(self) -> constants.StatusCode:
        """Last status code returned for an operation with this Resource Manager

        :rtype: :class:`pyvisa.constants.StatusCode`
        """
        return self.visalib.get_last_status_in_session(self.session)

    def close(self) -> None:
        """Close the resource manager session.

        """
        try:
            logger.debug("Closing ResourceManager (session: %s)", self.session)
            # Cleanly close all resources when closing the manager.
            for resource in self._created_resources:
                resource.close()
            self.visalib.close(self.session)
            # mypy don't get that we can set a value we cannot get
            self.session = None  # type: ignore
            self.visalib.resource_manager = None
        except errors.InvalidSession:
            pass

    def list_resources(self, query: str = "?*::INSTR") -> Tuple[str, ...]:
        """Returns a tuple of all connected devices matching query.

        note: The query uses the VISA Resource Regular Expression syntax - which is not the same
              as the Python regular expression syntax. (see below)

            The VISA Resource Regular Expression syntax is defined in the VISA Library specification:
            http://www.ivifoundation.org/docs/vpp43.pdf

            Symbol      Meaning
            ----------  ----------

            ?           Matches any one character.

            \           Makes the character that follows it an ordinary character
                        instead of special character. For example, when a question
                        mark follows a backslash (\?), it matches the ? character
                        instead of any one character.

            [list]      Matches any one character from the enclosed list. You can
                        use a hyphen to match a range of characters.

            [^list]     Matches any character not in the enclosed list. You can use
                        a hyphen to match a range of characters.

            *           Matches 0 or more occurrences of the preceding character or
                        expression.

            +           Matches 1 or more occurrences of the preceding character or
                        expression.

            Exp|exp     Matches either the preceding or following expression. The or
                        operator | matches the entire expression that precedes or
                        follows it and not just the character that precedes or follows
                        it. For example, VXI|GPIB means (VXI)|(GPIB), not VX(I|G)PIB.

            (exp)       Grouping characters or expressions.

            Thus the default query, '?*::INSTR', matches any sequences of characters ending
            ending with '::INSTR'.

        :param query: a VISA Resource Regular Expression used to match devices.

        """

        return self.visalib.list_resources(self.session, query)

    def list_resources_info(self, query: str = "?*::INSTR") -> Dict[str, ResourceInfo]:
        """Returns a dictionary mapping resource names to resource extended
        information of all connected devices matching query.

        For details of the VISA Resource Regular Expression syntax used in query,
        refer to list_resources().

        :param query: a VISA Resource Regular Expression used to match devices.
        :return: Mapping of resource name to ResourceInfo
        :rtype: dict[str, :class:`pyvisa.highlevel.ResourceInfo`]
        """

        return dict(
            (resource, self.resource_info(resource))
            for resource in self.list_resources(query)
        )

    def list_opened_resources(self) -> List[Resource]:
        """Returns a list of all the opened resources.

        :return: List of resources
        :rtype: list[:class:`pyvisa.resources.resource.Resource`]
        """
        opened = []
        for resource in self._created_resources:
            try:
                resource.session
            except errors.InvalidSession:
                pass
            else:
                opened.append(resource)
        return opened

    def resource_info(self, resource_name: str, extended: bool = True) -> ResourceInfo:
        """Get the (extended) information of a particular resource.

        :param resource_name: Unique symbolic name of a resource.

        :rtype: :class:`pyvisa.highlevel.ResourceInfo`
        """

        if extended:
            ret, err = self.visalib.parse_resource_extended(self.session, resource_name)
        else:
            ret, err = self.visalib.parse_resource(self.session, resource_name)

        return ret

    def open_bare_resource(
        self,
        resource_name: str,
        access_mode: constants.AccessModes = constants.AccessModes.no_lock,
        open_timeout: int = constants.VI_TMO_IMMEDIATE,
    ) -> Tuple[VISASession, constants.StatusCode]:
        """Open the specified resource without wrapping into a class

        :param resource_name: Name or alias of the resource to open.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int

        :return: Unique logical identifier reference to a session.
        """
        return self.visalib.open(self.session, resource_name, access_mode, open_timeout)

    def open_resource(
        self,
        resource_name: str,
        access_mode: constants.AccessModes = constants.AccessModes.no_lock,
        open_timeout: int = constants.VI_TMO_IMMEDIATE,
        resource_pyclass: Optional[Type[Resource]] = None,
        **kwargs: Any,
    ) -> Resource:
        """Return an instrument for the resource name.

        :param resource_name: Name or alias of the resource to open.
        :param access_mode: Specifies the mode by which the resource is to be accessed.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: If the ``access_mode`` parameter requests a lock, then this parameter specifies the
                             absolute time period (in milliseconds) that the resource waits to get unlocked before this
                             operation returns an error.
        :type open_timeout: int
        :param resource_pyclass: Resource Python class to use to instantiate the Resource.
                                 Defaults to None: select based on the resource name.
        :param kwargs: Keyword arguments to be used to change instrument attributes
                       after construction.

        :rtype: :class:`pyvisa.resources.Resource`
        """

        if resource_pyclass is None:
            info = self.resource_info(resource_name, extended=True)

            try:
                # When using querying extended resource info the resource_class is not
                # None
                resource_pyclass = self._resource_classes[
                    (info.interface_type, info.resource_class)  # type: ignore
                ]
            except KeyError:
                resource_pyclass = self._resource_classes[
                    (constants.InterfaceType.unknown, "")
                ]
                logger.warning(
                    "There is no class defined for %r. Using Resource",
                    (info.interface_type, info.resource_class),
                )

        res = resource_pyclass(self, resource_name)
        for key in kwargs.keys():
            try:
                getattr(res, key)
                present = True
            except AttributeError:
                present = False
            except errors.InvalidSession:
                present = True

            if not present:
                raise ValueError(
                    "%r is not a valid attribute for type %s"
                    % (key, res.__class__.__name__)
                )

        res.open(access_mode, open_timeout)

        for key, value in kwargs.items():
            setattr(res, key, value)

        self._created_resources.add(res)

        return res

    def get_instrument(
        self,
        resource_name: str,
        access_mode: constants.AccessModes = constants.AccessModes.no_lock,
        open_timeout: int = constants.VI_TMO_IMMEDIATE,
        resource_pyclass: Type[Resource] = None,
        **kwargs: Any,
    ) -> Resource:
        """Return an instrument for the resource name.

        :param resource_name: name or alias of the resource to open.
        :param access_mode: access mode.
        :type access_mode: :class:`pyvisa.constants.AccessModes`
        :param open_timeout: time out to open.
        :param resource_pyclass: resource python class to use to instantiate the Resource.
                                 Defaults to None: select based on the resource name.
        :param kwargs: keyword arguments to be used to change instrument attributes
                       after construction.

        :rtype: :class:`pyvisa.resources.Resource`
        """
        warnings.warn(
            "get_instrument is deprecated and will be removed in "
            "1.12, use open_resource instead.",
            FutureWarning,
        )
        return self.open_resource(
            resource_name, access_mode, open_timeout, resource_pyclass, **kwargs
        )
