# -*- coding: utf-8 -*-
"""Functions and classes to parse and assemble resource name.

:copyright: 2014-2020 by PyVISA Authors, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.

"""
import contextlib
import re
from collections import defaultdict, namedtuple
from typing import Callable, Dict, Iterable, List, NewType, Optional, Set, Tuple, Type

from . import constants, errors, logger

#: Interface types for which a subclass of ResourName exists
_INTERFACE_TYPES: Set[str] = set()

#: Resource Class for Interface type
_RESOURCE_CLASSES: Dict[str, Set[str]] = defaultdict(set)

#: Subclasses of ResourceName matching an interface type, resource class pair
_SUBCLASSES: Dict[Tuple[str, str], Type["ResourceName"]] = {}

# DEFAULT Resource Class for a given interface type.
_DEFAULT_RC: Dict[str, str] = {}


class InvalidResourceName(ValueError):
    """Exception raised when the resource name cannot be parsed."""

    def __init__(self, msg: str) -> None:
        self.msg = msg

    @classmethod
    def bad_syntax(
        cls, syntax: str, resource_name: str, ex: Exception = None
    ) -> "InvalidResourceName":
        """Build an exception when the resource name cannot be parsed."""
        if ex:
            msg = "The syntax is '%s' (%s)." % (syntax, ex)
        else:
            msg = "The syntax is '%s'." % syntax

        msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    @classmethod
    def subclass_notfound(
        cls, interface_type_resource_class: Tuple[str, str], resource_name: str = None,
    ) -> "InvalidResourceName":
        """Build an exception when no parser has been registered for a pair.

        """

        msg = "Parser not found for: %s." % (interface_type_resource_class,)

        if resource_name:
            msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    @classmethod
    def rc_notfound(
        cls, interface_type: str, resource_name: str = None
    ) -> "InvalidResourceName":
        """Build an exception when no resource class is provided and no default is found.

        """

        msg = (
            "Resource class for %s not provided and default not found." % interface_type
        )

        if resource_name:
            msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    def __str__(self) -> str:
        return self.msg


def register_subclass(cls: Type["ResourceName"]) -> Type["ResourceName"]:
    """Register a subclass for a given interface type and resource class."""

    key = cls.interface_type, cls.resource_class

    if key in _SUBCLASSES:
        raise ValueError("Class already registered for %s and %s" % key)

    _SUBCLASSES[(cls.interface_type, cls.resource_class)] = cls

    _INTERFACE_TYPES.add(cls.interface_type)
    _RESOURCE_CLASSES[cls.interface_type].add(cls.resource_class)

    if cls.is_rc_optional:
        if cls.interface_type in _DEFAULT_RC:
            raise ValueError("Default already specified for %s" % cls.interface_type)
        _DEFAULT_RC[cls.interface_type] = cls.resource_class

    return cls


class ResourceName(object):
    """Base class for ResourceNames to be used as a mixin."""

    #: Interface type string
    interface_type: str = ""

    #: Resource class string
    resource_class: str = ""

    #: Specifices if the resource class part of the string is optional.
    is_rc_optional: bool = False

    #: Formatting string for canonical
    _canonical_fmt: str = ""

    #: VISA syntax for resource
    _visa_syntax: str = ""

    #: Resource name provided by the user (not empty only when parsing)
    user: str = ""

    #: Common field to all resources
    board: str

    @property
    def interface_type_const(self) -> constants.InterfaceType:
        try:
            return getattr(constants.InterfaceType, self.interface_type.lower())
        except:
            return constants.InterfaceType.unknown

    @classmethod
    def from_string(cls, resource_name: str) -> "ResourceName":
        """Parse a resource name and return a ResourceName

        Parameters
        ----------
        resource_name : str
            Name of the resource

        Raises
        ------
        InvalidResourceName
            Raised if the resource name is invalid.

        """
        # TODO Remote VISA

        uname = resource_name.upper()

        for interface_type in _INTERFACE_TYPES:

            # Loop through all known interface types until we found one
            # that matches the beginning of the resource name
            if not uname.startswith(interface_type):
                continue

            parts: List[str]
            if len(resource_name) == len(interface_type):
                parts = []
            else:
                parts = resource_name[len(interface_type) :].split("::")

            # Try to match the last part of the resource name to
            # one of the known resource classes for the given interface type.
            # If not possible, use the default resource class
            # for the given interface type.
            if parts and parts[-1] in _RESOURCE_CLASSES[interface_type]:
                parts, resource_class = parts[:-1], parts[-1]
            else:
                try:
                    resource_class = _DEFAULT_RC[interface_type]
                except KeyError:
                    raise InvalidResourceName.rc_notfound(interface_type, resource_name)

            # Look for the subclass
            try:
                subclass = _SUBCLASSES[(interface_type, resource_class)]
            except KeyError:
                raise InvalidResourceName.subclass_notfound(
                    (interface_type, resource_class), resource_name
                )

            # And create the object
            try:
                rn = subclass.from_parts(*parts)
                rn.user = resource_name
                return rn
            except ValueError as ex:
                raise InvalidResourceName.bad_syntax(
                    subclass._visa_syntax, resource_name, ex
                )

        raise InvalidResourceName(
            "Could not parse %s: unknown interface type" % resource_name
        )

    @classmethod
    def from_kwargs(cls, **kwargs) -> "ResourceName":
        """Build a resource from keyword arguments."""
        interface_type = kwargs.pop("interface_type")

        if interface_type not in _INTERFACE_TYPES:
            raise InvalidResourceName("Unknown interface type: %s" % interface_type)

        try:
            resource_class = kwargs.pop("resource_class", _DEFAULT_RC[interface_type])
        except KeyError:
            raise InvalidResourceName.rc_notfound(interface_type)

        # Look for the subclass
        try:
            subclass = _SUBCLASSES[(interface_type, resource_class)]
        except KeyError:
            raise InvalidResourceName.subclass_notfound(
                (interface_type, resource_class)
            )

        # And create the object
        try:
            return subclass(**kwargs)
        except ValueError as ex:
            raise InvalidResourceName(str(ex))

    # Implemented when building concrete subclass in build_rn_class
    @classmethod
    def from_parts(cls, *parts):
        ...

    def __str__(self):
        return self._canonical_fmt.format(self)


def build_rn_class(
    interface_type: str,
    resource_parts: Tuple[Tuple[str, Optional[str]], ...],
    resource_class: str,
    is_rc_optional: bool = True,
) -> Type[ResourceName]:
    """Builds a resource name class by mixing a named tuple and ResourceName.

    It also registers the class.

    The field names are changed to lower case and the spaces replaced
    by underscores ('_').

    Parameters
    -----------
    interface_type : str
        The interface type the built class will be used for.
    resource_parts : Tuple[Tuple[str, Optional[str]], ...]
        Each of the parts of the resource name indicating name and default
        value. Use None for mandatory fields.
    resource_class : str
        The resource class the built class will be used for.
    is_rc_optional : bool, optional
        Indicates if the resource class part is optional.

    Returns
    -------
    Type[ResourceName]
        ResourceName subclass customized for the specified interface type and
        resource class.

    """

    interface_type = interface_type.upper()
    resource_class = resource_class.upper()

    syntax = interface_type
    fmt = interface_type
    fields: List[str] = []

    # Contains the resource parts but using python friendly names
    # (all lower case and replacing spaces by underscores)
    p_resource_parts = []

    kwdoc = []

    # Assemble the syntax and format string based on the resource parts
    for ndx, (name, default_value) in enumerate(resource_parts):
        pname = name.lower().replace(" ", "_")
        fields.append(pname)
        p_resource_parts.append((pname, default_value))

        sep = "::" if ndx else ""

        fmt += sep + "{0.%s}" % pname

        if default_value is None:
            syntax += sep + name
        else:
            syntax += "[" + sep + name + "]"

        kwdoc.append(
            "- %s (%s)"
            % (pname, "required" if default_value is None else default_value)
        )

    fmt += "::" + resource_class

    if not is_rc_optional:
        syntax += "::" + resource_class
    else:
        syntax += "[" + "::" + resource_class + "]"

    # too dynamic for Mypy
    class _C(namedtuple("Internal", fields), ResourceName):  # type: ignore
        """%s %s"

        Can be created with the following keyword only arguments:
            %s

        Format :
            %s

        """ % (
            resource_class,
            interface_type,
            "    \n".join(kwdoc),
            syntax,
        )

        def __new__(cls, **kwargs):
            new_kwargs = dict(p_resource_parts, **kwargs)

            for key, value in new_kwargs.items():
                if value is None:
                    raise ValueError(key + " is a required parameter")

            return super(_C, cls).__new__(cls, **new_kwargs)

        @classmethod
        def from_parts(cls, *parts):
            """Construct a resource name from a list of parts."""

            if len(parts) < sum(1 for _, v in p_resource_parts if v is not None):
                raise ValueError("not enough parts")
            elif len(parts) > len(p_resource_parts):
                raise ValueError("too many parts")

            (k, default), rp = p_resource_parts[0], p_resource_parts[1:]

            # The first part (just after the interface_type) is the only
            # optional part which can be empty and therefore the
            # default value should be used.
            p, pending = parts[0], parts[1:]
            kwargs = {k: default if p == "" else p}

            # The rest of the parts are consumed when mandatory elements are required.
            while len(pending) < len(rp):
                (k, default), rp = rp[0], rp[1:]
                if default is None:
                    # This is impossible as far as I can tell for currently implemented
                    # resource names
                    if not parts:
                        raise ValueError(k + " part is mandatory")  # pragma: no cover
                    p, pending = pending[0], pending[1:]
                    if not p:
                        raise ValueError(k + " part is mandatory")
                    kwargs[k] = p
                else:
                    kwargs[k] = default

            # When the length of the pending provided and resource parts
            # are equal, we just consume everything.
            kwargs.update((k, p) for (k, v), p in zip(rp, pending))

            return cls(**kwargs)

    _C.interface_type = interface_type
    _C.resource_class = resource_class
    _C.is_rc_optional = is_rc_optional
    _C._canonical_fmt = fmt
    _C._visa_syntax = syntax

    _C.__name__ = str(interface_type + resource_class.title())

    return register_subclass(_C)


# Build subclasses for each resource

# Reference for the GPIB secondary address
# https://www.mathworks.com/help/instrument/secondaryaddress.html
GPIBInstr = build_rn_class(
    "GPIB",
    (("board", "0"), ("primary address", None), ("secondary address", "0")),
    "INSTR",
)

GPIBIntfc = build_rn_class("GPIB", (("board", "0"),), "INTFC", False)

ASRLInstr = build_rn_class("ASRL", (("board", "0"),), "INSTR")

TCPIPInstr = build_rn_class(
    "TCPIP",
    (("board", "0"), ("host address", None), ("LAN device name", "inst0"),),
    "INSTR",
)

TCPIPSocket = build_rn_class(
    "TCPIP", (("board", "0"), ("host address", None), ("port", None),), "SOCKET", False
)

USBInstr = build_rn_class(
    "USB",
    (
        ("board", "0"),
        ("manufacturer ID", None),
        ("model code", None),
        ("serial number", None),
        ("USB interface number", "0"),
    ),
    "INSTR",
)

USBRaw = build_rn_class(
    "USB",
    (
        ("board", "0"),
        ("manufacturer ID", None),
        ("model code", None),
        ("serial number", None),
        ("USB interface number", "0"),
    ),
    "RAW",
    False,
)

PXIBackplane = build_rn_class(
    "PXI", (("interface", "0"), ("chassis number", None)), "BACKPLANE", False
)

PXIMemacc = build_rn_class("PXI", (("interface", "0"),), "MEMACC", False)

VXIBackplane = build_rn_class(
    "VXI", (("board", "0"), ("VXI logical address", "0")), "BACKPLANE", False
)

VXIInstr = build_rn_class(
    "VXI", (("board", "0"), ("VXI logical address", None)), "INSTR", True
)

VXIMemacc = build_rn_class("VXI", (("board", "0"),), "MEMACC", False)

VXIServant = build_rn_class("VXI", (("board", "0"),), "SERVANT", False)

# TODO 3 types of PXI INSTR
# TODO ENET-Serial INSTR
# TODO Remote NI-VISA


def assemble_canonical_name(**kwargs) -> str:
    """Build the canonical resource name from a set of keyword arguments."""
    return str(ResourceName.from_kwargs(**kwargs))


def to_canonical_name(resource_name: str) -> str:
    """Parse a resource name and return the canonical version."""
    return str(ResourceName.from_string(resource_name))


parse_resource_name = ResourceName.from_string


def filter(resources: Iterable[str], query: str) -> Tuple[str, ...]:
    r"""Filter a list of resources according to a query expression.

    The search criteria specified in the query parameter has two parts:
      1. a VISA regular expression over a resource string.
      2. optional logical expression over attribute values
         (not implemented in this function, see below).

    .. note: The VISA regular expression syntax is not the same as the
             Python regular expression syntax. (see below)

    The regular expression is matched against the resource strings of resources
    known to the VISA Resource Manager. If the resource string matches the
    regular expression, the attribute values of the resource are then matched
    against the expression over attribute values. If the match is successful,
    the resource has met the search criteria and gets added to the list of
    resources found.

    By using the optional attribute expression, you can construct flexible
    and powerful expressions with the use of logical ANDs (&&), ORs(||),
    and NOTs (!). You can use equal (==) and unequal (!=) comparators to
    compare attributes of any type, and other inequality comparators
    (>, <, >=, <=) to compare attributes of numeric type. Use only global
    attributes in the attribute expression. Local attributes are not allowed
    in the logical expression part of the expr parameter.


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


    """

    if "{" in query:
        query, _ = query.split("{")
        logger.warning(
            "optional part of the query expression not supported. " "See filter2"
        )

    try:
        query = query.replace("?", ".")
        matcher = re.compile(query, re.IGNORECASE)
    except re.error:
        raise errors.VisaIOError(constants.VI_ERROR_INV_EXPR)

    return tuple(res for res in resources if matcher.match(res))


def filter2(
    resources: Iterable[str],
    query: str,
    open_resource: Callable[[str], "resources.Resource"],
) -> List[str]:
    """Filter a list of resources according to a query expression.

    It accepts the optional part of the expression.

    .. warning: This function is experimental and unsafe as it uses eval,
                It also might require to open the resource.

    Parameters
    ----------
    resources : Iterable[str]
        Iterable of resource name to filter.

    query : str
        The pattern to use for filtering

    open_resource : Callable[[str], "resources.Resource"]
        Function to open a resource (typically ResourceManager().open_resource)

    """
    optional: Optional[str]
    if "{" in query:
        try:
            query, optional = query.split("{")
            optional, _ = optional.split("}")
        except ValueError:
            raise errors.VisaIOError(constants.VI_ERROR_INV_EXPR)
    else:
        optional = None

    filtered = filter(resources, query)

    if not optional:
        return list(filtered)

    optional = optional.replace("&&", "and").replace("||", "or").replace("!", "not ")
    optional = optional.replace("VI_", "res.VI_")

    class AttrGetter:
        def __init__(self, resource_name):
            self.resource_name = resource_name
            self.parsed = parse_resource_name(resource_name)
            self.resource = None

        def __getattr__(self, item):
            if item == "VI_ATTR_INTF_NUM":
                return int(self.parsed.board)
            elif item == "VI_ATTR_MANF_ID":
                if not isinstance(self.parsed, (USBInstr, USBRaw)):
                    raise self.raise_missing_attr(item)
                else:
                    return self.parsed.manufacturer_id
            elif item == "VI_ATTR_MODEL_CODE":
                if not isinstance(self.parsed, (USBInstr, USBRaw)):
                    raise self.raise_missing_attr(item)
                else:
                    return self.parsed.model_code
            elif item == "VI_ATTR_USB_SERIAL_NUM":
                if not isinstance(self.parsed, (USBInstr, USBRaw)):
                    raise self.raise_missing_attr(item)
                else:
                    return self.parsed.serial_number
            elif item == "VI_ATTR_USB_INTFC_NUM":
                if not isinstance(self.parsed, (USBInstr, USBRaw)):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.board)
            elif item == "VI_ATTR_TCPIP_ADDR":
                if not isinstance(self.parsed, (TCPIPInstr, TCPIPSocket)):
                    raise self.raise_missing_attr(item)
                else:
                    return self.parsed.host_address
            elif item == "VI_ATTR_TCPIP_DEVICE_NAME":
                if not isinstance(self.parsed, TCPIPInstr):
                    raise self.raise_missing_attr(item)
                else:
                    return self.parsed.lan_device_name
            elif item == "VI_ATTR_TCPIP_PORT":
                if not isinstance(self.parsed, TCPIPSocket):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.port)
            elif item == "VI_ATTR_GPIB_PRIMARY_ADDR":
                if not isinstance(self.parsed, GPIBInstr):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.primary_address)
            elif item == "VI_ATTR_GPIB_SECONDARY_ADDR":
                if not isinstance(self.parsed, GPIBInstr):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.secondary_address)
            elif item == "VI_ATTR_PXI_CHASSIS":
                if not isinstance(self.parsed, PXIBackplane):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.chassis_number)
            elif item == "VI_ATTR_MAINFRAME_LA":
                if not isinstance(self.parsed, (VXIInstr, VXIBackplane)):
                    raise self.raise_missing_attr(item)
                else:
                    return int(self.parsed.vxi_logical_address)

            if self.resource is None:
                self.resource = open_resource(self.resource_name)

            return self.resource.get_visa_attribute(item)

        def raise_missing_attr(self, item):
            raise errors.VisaIOError(constants.VI_ERROR_NSUP_ATTR)

    @contextlib.contextmanager
    def open_close(resource_name):
        getter = AttrGetter(resource_name)
        yield getter
        if getter.resource is not None:
            getter.resource.close()

    selected = []
    for rn in filtered:
        with open_close(rn) as getter:
            try:
                if eval(optional, None, dict(res=getter)):
                    selected.append(rn)
            except Exception:
                logger.exception("Failed to evaluate %s on %s", optional, rn)

    return selected
