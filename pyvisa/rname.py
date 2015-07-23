# -*- coding: utf-8 -*-
"""
    pyvisa.rname
    ~~~~~~~~~~~~

    Functions and classes to parse and assemble resource name.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import re
from collections import namedtuple, defaultdict

from pyvisa import constants

# :type: set[str]
_INTERFACE_TYPES = set()

# Resource Class for Interface type
# :type: dict[str, set[str]]
_RESOURCE_CLASSES = defaultdict(set)

# :type: dict[(str, str), ResourceName]
_SUBCLASSES = {}

# DEFAULT Resource Class for a given interface type.
# :type: dict[str, str]
_DEFAULT_RC = {}


class InvalidResourceName(ValueError):
    """Exception raised when the resource name cannot be parsed.
    """

    def __init__(self, msg):
        self.msg = msg

    @classmethod
    def bad_syntax(cls, syntax, resource_name, ex=None):
        """Exception used when the resource name cannot be parsed.
        """

        if ex:
            msg = "The syntax is '%s' (%s)." % (syntax, ex)
        else:
            msg = "The syntax is '%s'." % syntax

        msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    @classmethod
    def subclass_notfound(cls, interface_type_resource_class,
                          resource_name=None):
        """Exception used when the subclass for a given interface type / resource class pair
        cannot be found.
        """

        msg = "Parser for not found (%s)." % interface_type_resource_class

        if resource_name:
            msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    @classmethod
    def rc_notfound(cls, interface_type, resource_name=None):
        """Exception used when no resource class is provided and no default is found.
        """

        msg = "Resource class for %s not provided and default not found." % interface_type

        if resource_name:
            msg = "Could not parse '%s'. %s" % (resource_name, msg)

        return cls(msg)

    def __str__(self):
        return self.msg


def register_subclass(cls):
    """Register a subclass for a given interface type and resource class.
    """

    key = cls.interface_type, cls.resource_class

    if key in _SUBCLASSES:
        raise ValueError('Class already registered for %s and %s' % key)

    _SUBCLASSES[(cls.interface_type, cls.resource_class)] = cls

    _INTERFACE_TYPES.add(cls.interface_type)
    _RESOURCE_CLASSES[cls.interface_type].add(cls.resource_class)

    if cls.is_rc_optional:
        if cls.interface_type in _DEFAULT_RC:
            raise ValueError('Default already specified for %s' %
                             cls.interface_type)
        _DEFAULT_RC[cls.interface_type] = cls.resource_class

    return cls


class ResourceName(object):
    """Base class for ResourceNames to be used as a Mixin
    """

    # Interface type string
    interface_type = ''

    # Resource class string
    resource_class = ''

    # Specifices if the resource class part of the string is optional.
    is_rc_optional = False

    # Formatting string for canonical
    _canonical_fmt = ''

    # VISA syntax for resource
    _visa_syntax = ''

    # Resource name provided by the user (not empty only when parsing)
    user = ''

    @property
    def interface_type_const(self):
        try:
            return getattr(constants.InterfaceType, self.interface_type.lower())
        except:
            return constants.InterfaceType.unknown

    @classmethod
    def from_string(cls, resource_name):
        """Parse a resource name and return a ResourceName

        :type resource_name: str
        :rtype: ResourceName

        :raises InvalidResourceName: if the resource name is invalid.
        """
        # TODO Remote VISA

        uname = resource_name.upper()

        for interface_type in _INTERFACE_TYPES:

            # Loop through all known interface types until we found one
            # that matches the beginning of the resource name
            if not uname.startswith(interface_type):
                continue

            if len(resource_name) == len(interface_type):
                parts = ()
            else:
                parts = resource_name[len(interface_type):].split('::')

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
                    raise InvalidResourceName.rc_notfound(interface_type,
                                                          resource_name)

            # Look for the subclass
            try:
                subclass = _SUBCLASSES[(interface_type, resource_class)]
            except KeyError:
                raise InvalidResourceName.subclass_notfound(
                    (interface_type, resource_class), resource_name)

            # And create the object
            try:
                rn = subclass.from_parts(*parts)
                rn.user = resource_name
                return rn
            except ValueError as ex:
                raise InvalidResourceName.bad_syntax(subclass._visa_syntax,
                                                     resource_name, ex)

        raise InvalidResourceName('Could not parse %s: unknown interface type'
                                  % resource_name)

    @classmethod
    def from_kwargs(cls, **kwargs):
        interface_type = kwargs.pop('interface_type')

        try:
            resource_class = kwargs.pop('resource_class',
                                        _DEFAULT_RC[interface_type])
        except KeyError:
            raise InvalidResourceName.rc_notfound(interface_type)

        # Look for the subclass
        try:
            subclass = _SUBCLASSES[(interface_type, resource_class)]
        except KeyError:
            raise InvalidResourceName.subclass_notfound(
                (interface_type, resource_class))

        # And create the object
        try:
            return subclass(**kwargs)
        except ValueError as ex:
            raise InvalidResourceName(str(ex))

    def __str__(self):
        return self._canonical_fmt.format(self)


def build_rn_class(interface_type, resource_parts, resource_class,
                   is_rc_optional=True):
    """Builds a resource name class by mixing a named tuple and ResourceName.

    It also registers the class.

    The field names are changed to lower case and the spaces replaced
    by underscores ('_').

    :param interface_type: the interface type
    :type: interface_type: str
    :param resource_parts: each of the parts of the resource name indicating
                           name and default value.
                           Use None for mandatory fields.
    :type resource_parts: tuple[(str, str)]
    :param resource_class: the resource class
    :type resource_class: str
    :param is_rc_optional: indicates if the resource class part is optional
    :type is_rc_optional: boolean.
    """

    interface_type = interface_type.upper()
    resource_class = resource_class.upper()

    syntax = interface_type
    fmt = interface_type
    fields = []

    # Contains the resource parts but using python friendly names
    # (all lower case and replacing spaces by underscores)
    p_resource_parts = []

    kwdoc = []

    # Assemble the syntax and format string based on the resource parts
    for ndx, (name, default_value) in enumerate(resource_parts):
        pname = name.lower().replace(' ', '_')
        fields.append(pname)
        p_resource_parts.append((pname, default_value))

        sep = '::' if ndx else ''

        fmt += sep + '{0.%s}' % pname

        if default_value is None:
            syntax += sep + name
        else:
            syntax += '[' + sep + name + ']'

        kwdoc.append('- %s (%s)' % (pname, 'required' if default_value is None
                                    else default_value))

    fmt += '::' + resource_class

    if not is_rc_optional:
        syntax += '::' + resource_class
    else:
        syntax += '[' + '::' + resource_class + ']'

    class _C(namedtuple('Internal', ' '.join(fields)), ResourceName):
        """%s %s"

        Can be created with the following keyword only arguments:
            %s

        Format :
            %s
        """ % (resource_class, interface_type, '    \n'.join(kwdoc), syntax)

        def __new__(cls, **kwargs):
            new_kwargs = dict(p_resource_parts, **kwargs)

            for key, value in new_kwargs.items():
                if value is None:
                    raise ValueError(key + ' is a required parameter')

            return super(_C, cls).__new__(cls, **new_kwargs)

        @classmethod
        def from_parts(cls, *parts):

            if len(parts) < sum(1 for _, v in p_resource_parts
                                if v is not None):
                raise ValueError('not enough parts')
            elif len(parts) > len(p_resource_parts):
                raise ValueError('too many parts')

            (k, default), rp = p_resource_parts[0], p_resource_parts[1:]

            # The first part (just after the interface_type) is the only
            # optional part which can be and empty and therefore the
            # default value should be used.
            p, pending = parts[0], parts[1:]
            kwargs = {k: default if p == '' else p}

            # The rest of the parts are consumed when mandatory elements are required.
            while len(pending) < len(rp):
                (k, default), rp = rp[0], rp[1:]
                if default is None:
                    if not parts:
                        raise ValueError(k + ' part is mandatory')
                    p, pending = pending[0], pending[1:]
                    if not p:
                        raise ValueError(k + ' part is mandatory')
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

GPIBInstr = build_rn_class('GPIB',
                           (('board', '0'), ('primary address', None),
                            ('secondary address', constants.VI_NO_SEC_ADDR)),
                           'INSTR')

GPIBIntfc = build_rn_class('GPIB', (('board', '0'), ), 'INTFC', False)

ASRLInstr = build_rn_class('ASRL', (('board', '0'), ), 'INSTR')

TCPIPInstr = build_rn_class('TCPIP', (('board', '0'), ('host address', None),
                                      ('LAN device name', 'inst0'), ), 'INSTR')

TCPIPSocket = build_rn_class('TCPIP', (('board', '0'), ('host address', None),
                                       ('port', None), ), 'SOCKET', False)

USBInstr = build_rn_class('USB',
                          (('board', '0'), ('manufacturer ID', None),
                           ('model code', None), ('serial number', None),
                           ('USB interface number', '0')), 'INSTR')

USBRaw = build_rn_class('USB', (('board', '0'), ('manufacturer ID', None),
                                ('model code', None), ('serial number', None),
                                ('USB interface number', '0')), 'RAW', False)

PXIBackplane = build_rn_class('PXI', (('interface', '0'),
                                      ('chassis number', None)), 'BACKPLANE',
                              False)

PXIMemacc = build_rn_class('PXI', (('interface', '0'), ), 'MEMACC', False)

VXIBackplane = build_rn_class('VXI', (('board', '0'),
                                      ('VXI logical address', '0')),
                              'BACKPLANE', False)

VXIInstr = build_rn_class('VXI', (('board', '0'),
                                  ('VXI logical address', None)), 'INSTR',
                          True)

VXIMemacc = build_rn_class('VXI', (('board', '0'), ), 'MEMACC', False)

VXIServant = build_rn_class('VXI', (('board', '0'), ), 'SERVANT', False)

# TODO 3 types of PXI INSTR
# TODO ENET-Serial INSTR
# TODO Remote NI-VISA


def assemble_canonical_name(**kwargs):
    """Given a set of keyword arguments defining a resource name,
    return the canonical resource name.
    """
    return str(ResourceName.from_kwargs(**kwargs))


def to_canonical_name(resource_name):
    """Parse a resource name and return the canonical version.

    :type resource_name: str
    :rtype: str
    """
    return str(ResourceName.from_string(resource_name))


parse_resource_name = ResourceName.from_string


def filter(resources, query):
    """Filter a list of resources according to a query expression.

    The search criteria specified in the query parameter has two parts:
      1. a VISA regular expression over a resource string.
      2. optional logical expression over attribute values (not implemented).

    :param resources: iterable of resources.
    :param query: query expression.
    """

    query = query.replace('?*', '.*')
    matcher = re.compile(query, re.IGNORECASE)

    return tuple(res for res in resources if matcher.match(res))
