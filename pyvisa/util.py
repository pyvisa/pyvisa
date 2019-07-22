# -*- coding: utf-8 -*-
"""
    pyvisa.util
    ~~~~~~~~~~~

    General utility functions.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import functools
import io
import os
import platform
import sys
import subprocess
import warnings
import inspect
from subprocess import check_output

from .compat import (string_types, OrderedDict, struct,
                     int_to_bytes, int_from_bytes, PYTHON3)
from . import __version__, logger


try:
    import numpy as np
except ImportError:
    np = None


def _use_numpy_routines(container):
    """Should optimized numpy routines be used to extract the data.

    """
    if np is None or container in (tuple, list):
        return False

    if (container is np.array or (inspect.isclass(container) and
                                  issubclass(container, np.ndarray))):
        return True

    return False


def read_user_library_path():
    """Return the library path stored in one of the following configuration files:

        <sys prefix>/share/pyvisa/.pyvisarc
        ~/.pyvisarc

    <sys prefix> is the site-specific directory prefix where the platform
    independent Python files are installed.

    Example configuration file:

        [Paths]
        visa library=/my/path/visa.so

    Return `None` if  configuration files or keys are not present.

    """
    try:
        from ConfigParser import (SafeConfigParser as ConfigParser,
                                  NoSectionError)
    except ImportError:
        from configparser import ConfigParser, NoSectionError

    config_parser = ConfigParser()
    files = config_parser.read([os.path.join(sys.prefix, "share", "pyvisa",
                                             ".pyvisarc"),
                                os.path.join(os.path.expanduser("~"),
                                             ".pyvisarc")])

    if not files:
        logger.debug('No user defined library files')
        return None

    logger.debug('User defined library files: %s' % files)
    try:
        return config_parser.get("Paths", "visa library")
    except (KeyError, NoSectionError):
        logger.debug('KeyError or NoSectionError while reading config file')
        return None


class LibraryPath(str):

    #: Architectural information (32, ) or (64, ) or (32, 64)
    _arch = None

    def __new__(cls, path, found_by='auto'):
        obj = super(LibraryPath, cls).__new__(cls, path)
        obj.path = path
        obj.found_by = found_by

        return obj

    @property
    def arch(self):
        if self._arch is None:
            try:
                self._arch = get_arch(self.path)
            except:
                self._arch = tuple()

        return self._arch

    @property
    def is_32bit(self):
        if not self.arch:
            return 'n/a'
        return 32 in self.arch

    @property
    def is_64bit(self):
        if not self.arch:
            return 'n/a'
        return 64 in self.arch

    @property
    def bitness(self):
        if not self.arch:
            return 'n/a'
        return ', '.join(str(a) for a in self.arch)


def warn_for_invalid_kwargs(keyw, allowed_keys):
    for key in keyw.keys():
        if key not in allowed_keys:
            warnings.warn('Keyword argument "%s" unknown' % key, stacklevel=3)


def filter_kwargs(keyw, selected_keys):
    result = {}
    for key, value in keyw.items():
        if key in selected_keys:
            result[key] = value
    return result


def split_kwargs(keyw, self_keys, parent_keys, warn=True):
    self_kwargs = dict()
    parent_kwargs = dict()
    self_keys = set(self_keys)
    parent_keys = set(parent_keys)
    all_keys = self_keys | parent_keys
    for key, value in keyw.items():
        if warn and key not in all_keys:
            warnings.warn('Keyword argument "%s" unknown' % key, stacklevel=3)
        if key in self_keys:
            self_kwargs[key] = value
        if key in parent_keys:
            parent_kwargs[key] = value

    return self_kwargs, parent_kwargs


_converters = {
    's': str,
    'b': functools.partial(int, base=2),
    'c': chr,
    'd': int,
    'o': functools.partial(int, base=8),
    'x': functools.partial(int, base=16),
    'X': functools.partial(int, base=16),
    'e': float,
    'E': float,
    'f': float,
    'F': float,
    'g': float,
    'G': float,
}

_np_converters = {
    'd': 'i',
    'e': 'f',
    'E': 'f',
    'f': 'f',
    'F': 'f',
    'g': 'f',
    'G': 'f',
}


def from_ascii_block(ascii_data, converter='f', separator=',', container=list):
    """Parse ascii data and return an iterable of numbers.

    :param ascii_data: data to be parsed.
    :type ascii_data: str
    :param converter: function used to convert each value.
                      Defaults to float
    :type converter: callable
    :param separator: a callable that split the str into individual elements.
                      If a str is given, data.split(separator) is used.
    :type: separator: (str) -> collections.Iterable[T] | str
    :param container: container type to use for the output data.
    """
    if (_use_numpy_routines(container) and
            isinstance(converter, string_types) and
            isinstance(separator, string_types) and
            converter in _np_converters):
        return np.fromstring(ascii_data, _np_converters[converter],
                             sep=separator)

    if isinstance(converter, string_types):
        try:
            converter = _converters[converter]
        except KeyError:
            raise ValueError('Invalid code for converter: %s not in %s' %
                             (converter, str(tuple(_converters.keys()))))

    if isinstance(separator, string_types):
        data = ascii_data.split(separator)
    else:
        data = separator(ascii_data)

    return container([converter(raw_value) for raw_value in data])


def to_ascii_block(iterable, converter='f', separator=','):
    """Turn an iterable of numbers in an ascii block of data.

    :param iterable: data to be parsed.
    :type iterable: collections.Iterable[T]
    :param converter: function used to convert each value.
                      String formatting codes are also accepted.
                      Defaults to str.
    :type converter: callable | str
    :param separator: a callable that split the str into individual elements.
                      If a str is given, data.split(separator) is used.
    :type: separator: (collections.Iterable[T]) -> str | str

    :rtype: str
    """

    if isinstance(separator, string_types):
        separator = separator.join

    if isinstance(converter, string_types):
        converter = '%' + converter
        block = separator(converter % val for val in iterable)
    else:
        block = separator(converter(val) for val in iterable)
    return block


def parse_binary(bytes_data, is_big_endian=False, is_single=False):
    """Parse ascii data and return an iterable of numbers.

    To be deprecated in 1.7

    :param bytes_data: data to be parsed.
    :param is_big_endian: boolean indicating the endianness.
    :param is_single: boolean indicating the type (if not is double)
    :return:
    """
    warnings.warn('parse_binary is deprecated and will be removed in '
                  '1.10, use read_ascii_values or read_binary_values '
                  'instead.', FutureWarning)
    data = bytes_data

    hash_sign_position = bytes_data.find(b"#")
    if hash_sign_position == -1:
        raise ValueError('Could not find valid hash position')

    if hash_sign_position > 0:
        data = data[hash_sign_position:]

    data_1 = data[1:2].decode('ascii')

    if data_1.isdigit() and int(data_1) > 0:
        number_of_digits = int(data_1)
        # I store data and data_length in two separate variables in case
        # that data is too short.  FixMe: Maybe I should raise an error if
        # it's too long and the trailing part is not just CR/LF.
        data_length = int(data[2:2 + number_of_digits])
        data = data[2 + number_of_digits:2 + number_of_digits + data_length]
    else:
        data = data[2:]
        if data[-1:].decode('ascii') == "\n":
            data = data[:-1]
        data_length = len(data)

    if is_big_endian:
        endianess = ">"
    else:
        endianess = "<"

    try:
        if is_single:
            fmt = endianess + str(data_length // 4) + 'f'
        else:
            fmt = endianess + str(data_length // 8) + 'd'

        result = list(struct.unpack(fmt, data))
    except struct.error:
        raise ValueError("Binary data itself was malformed")

    return result


def parse_ieee_block_header(block):
    """Parse the header of a IEEE block.

    Definite Length Arbitrary Block:
    #<header_length><data_length><data>

    The header_length specifies the size of the data_length field.
    And the data_length field specifies the size of the data.

    Indefinite Length Arbitrary Block:
    #0<data>

    In this case the data length returned will be 0. The actual length can be
    deduced from the block and the offset.

    :param block: IEEE block.
    :type block: bytes | bytearray
    :return: (offset, data_length)
    :rtype: (int, int)
    """
    begin = block.find(b'#')
    if begin < 0:
        raise ValueError("Could not find hash sign (#) indicating the start of"
                         " the block.")

    try:
        # int(block[begin+1]) != int(block[begin+1:begin+2]) in Python 3
        header_length = int(block[begin+1:begin+2])
    except ValueError:
        header_length = 0
    offset = begin + 2 + header_length

    if header_length > 0:
        # #3100DATA
        # 012345
        data_length = int(block[begin+2:offset])
    else:
        # #0DATA
        # 012
        data_length = 0

    return offset, data_length


def parse_hp_block_header(block, is_big_endian):
    """Parse the header of a HP block.

    Definite Length Arbitrary Block:
    #A<data_length><data>

    The header ia always 4 bytes long.
    The data_length field specifies the size of the data.

    :param block: HP block.
    :type block: bytes | bytearray
    :param is_big_endian: boolean indicating endianess.
    :return: (offset, data_length)
    :rtype: (int, int)

    """
    begin = block.find(b'#A')
    if begin < 0:
        raise ValueError("Could not find the standard block header (#A) "
                         "indicating the start of the block.")
    offset = begin + 4

    data_length = int_from_bytes(block[begin+2:offset],
                                 byteorder='big' if is_big_endian else 'little'
                                 )

    return offset, data_length


def from_ieee_block(block, datatype='f', is_big_endian=False, container=list):
    """Convert a block in the IEEE format into an iterable of numbers.

    Definite Length Arbitrary Block:
    #<header_length><data_length><data>

    The header_length specifies the size of the data_length field.
    And the data_length field specifies the size of the data.

    Indefinite Length Arbitrary Block:
    #0<data>

    :param block: IEEE block.
    :type block: bytes | bytearray
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :param container: container type to use for the output data.
    :return: items
    :rtype: type(container)
    """
    offset, data_length = parse_ieee_block_header(block)

    if data_length == 0:
        data_length = len(block) - offset - 1

    if len(block) < offset + data_length:
        raise ValueError("Binary data is incomplete. The header states %d data"
                         " bytes, but %d where received." %
                         (data_length, len(block) - offset))

    return from_binary_block(block, offset, data_length, datatype,
                             is_big_endian, container)


def from_hp_block(block, datatype='f', is_big_endian=False, container=list):
    """Convert a block in the HP format into an iterable of numbers.

    Definite Length Arbitrary Block:
    #A<data_length><data>

    The header ia always 4 bytes long.
    The data_length field specifies the size of the data.

    :param block: HP block.
    :type block: bytes | bytearray
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :param container: container type to use for the output data.
    :return: items
    :rtype: type(container)
    """
    offset, data_length = parse_hp_block_header(block, is_big_endian)

    if len(block) < offset + data_length:
        raise ValueError("Binary data is incomplete. The header states %d data"
                         " bytes, but %d where received." %
                         (data_length, len(block) - offset))

    return from_binary_block(block, offset, data_length, datatype,
                             is_big_endian, container)


def from_binary_block(block, offset=0, data_length=None, datatype='f',
                      is_big_endian=False, container=list):
    """Convert a binary block into an iterable of numbers.

    :param block: binary block.
    :type block: bytes | bytearray
    :param offset: offset at which the data block starts (default=0)
    :param data_length: size in bytes of the data block
                        (default=len(block) - offset)
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :param container: container type to use for the output data.
    :return: items
    :rtype: type(container)
    """
    if data_length is None:
        data_length = len(block) - offset

    element_length = struct.calcsize(datatype)
    array_length = int(data_length / element_length)

    endianess = '>' if is_big_endian else '<'

    if _use_numpy_routines(container):
        return np.frombuffer(block, endianess+datatype, array_length, offset)

    fullfmt = '%s%d%s' % (endianess, array_length, datatype)

    try:
        return container(struct.unpack_from(fullfmt, block, offset))
    except struct.error:
        raise ValueError("Binary data was malformed")


def to_binary_block(iterable, header, datatype, is_big_endian):
    """Convert an iterable of numbers into a block of data with a given header.

    :param iterable: an iterable of numbers.
    :param header: the header which should prefix the binary block
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :return: IEEE block.
    :rtype: bytes
    """
    array_length = len(iterable)

    endianess = '>' if is_big_endian else '<'
    fullfmt = '%s%d%s' % (endianess, array_length, datatype)

    if isinstance(header, string_types):
        header = bytes(header, 'ascii') if PYTHON3 else str(header)

    return header + struct.pack(fullfmt, *iterable)


def to_ieee_block(iterable, datatype='f', is_big_endian=False):
    """Convert an iterable of numbers into a block of data in the IEEE format.

    :param iterable: an iterable of numbers.
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :return: IEEE block.
    :rtype: bytes
    """
    array_length = len(iterable)
    element_length = struct.calcsize(datatype)
    data_length = array_length * element_length

    header = '%d' % data_length
    header = '#%d%s' % (len(header), header)

    return to_binary_block(iterable, header, datatype, is_big_endian)


def to_hp_block(iterable, datatype='f', is_big_endian=False):
    """Convert an iterable of numbers into a block of data in the HP format.

    :param iterable: an iterable of numbers.
    :param datatype: the format string for a single element. See struct module.
    :param is_big_endian: boolean indicating endianess.
    :return: IEEE block.
    :rtype: bytes
    """

    array_length = len(iterable)
    element_length = struct.calcsize(datatype)
    data_length = array_length * element_length

    header = b'#A' + (int_to_bytes(data_length, 2,
                                   'big' if is_big_endian else 'little'))

    return to_binary_block(iterable, header, datatype, is_big_endian)


def get_system_details(backends=True):
    """Return a dictionary with information about the system
    """
    buildno, builddate = platform.python_build()
    if sys.maxunicode == 65535:
        # UCS2 build (standard)
        unitype = 'UCS2'
    else:
        # UCS4 build (most recent Linux distros)
        unitype = 'UCS4'
    bits, linkage = platform.architecture()

    d = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'executable': sys.executable,
        'implementation': getattr(platform, 'python_implementation',
                                  lambda: 'n/a')(),
        'python': platform.python_version(),
        'compiler': platform.python_compiler(),
        'buildno': buildno,
        'builddate': builddate,
        'unicode': unitype,
        'bits': bits,
        'pyvisa': __version__,
        'backends': OrderedDict()
    }

    if backends:
        from . import highlevel
        for backend in highlevel.list_backends():
            if backend.startswith('pyvisa-'):
                backend = backend[7:]

            try:
                cls = highlevel.get_wrapper_class(backend)
            except Exception as e:
                d['backends'][backend] = ['Could not instantiate backend',
                                          '-> %s' % str(e)]
                continue

            try:
                d['backends'][backend] = cls.get_debug_info()
            except Exception as e:
                d['backends'][backend] = ['Could not obtain debug info',
                                          '-> %s' % str(e)]

    return d


def system_details_to_str(d, indent=''):
    """Return a str with the system details.
    """

    l = ['Machine Details:',
         '   Platform ID:    %s' % d.get('platform', 'n/a'),
         '   Processor:      %s' % d.get('processor', 'n/a'),
         '',
         'Python:',
         '   Implementation: %s' % d.get('implementation', 'n/a'),
         '   Executable:     %s' % d.get('executable', 'n/a'),
         '   Version:        %s' % d.get('python', 'n/a'),
         '   Compiler:       %s' % d.get('compiler', 'n/a'),
         '   Bits:           %s' % d.get('bits', 'n/a'),
         '   Build:          %s (#%s)' % (d.get('builddate', 'n/a'),
                                          d.get('buildno', 'n/a')),
         '   Unicode:        %s' % d.get('unicode', 'n/a'),
         '',
         'PyVISA Version: %s' % d.get('pyvisa', 'n/a'),
         '',
         ]

    def _to_list(key, value, indent_level=0):
        sp = ' ' * indent_level * 3

        if isinstance(value, string_types):
            if key:
                return ['%s%s: %s' % (sp, key, value)]
            else:
                return ['%s%s' % (sp, value)]

        elif isinstance(value, dict):
            if key:
                al = ['%s%s:' % (sp, key)]
            else:
                al = []

            for k, v in value.items():
                al.extend(_to_list(k, v, indent_level+1))
            return al

        elif isinstance(value, (tuple, list)):
            if key:
                al = ['%s%s:' % (sp, key)]
            else:
                al = []

            for v in value:
                al.extend(_to_list(None, v, indent_level+1))

            return al

    l.extend(_to_list('Backends', d['backends']))

    joiner = '\n' + indent
    return indent + joiner.join(l) + '\n'


def get_debug_info(to_screen=True):
    out = system_details_to_str(get_system_details())
    if not to_screen:
        return out
    print(out)


def pip_install(package):
    try:
        # noinspection PyPackageRequirements,PyUnresolvedReferences
        import pip
        return pip.main(['install', package])
    except ImportError:
        print(system_details_to_str(get_system_details()))
        raise RuntimeError('Please install pip to continue.')


machine_types = {
    0: 'UNKNOWN',
    0x014c: 'I386',
    0x0162: 'R3000',
    0x0166: 'R4000',
    0x0168: 'R10000',
    0x0169: 'WCEMIPSV2',
    0x0184: 'ALPHA',
    0x01a2: 'SH3',
    0x01a3: 'SH3DSP',
    0x01a4: 'SH3E',
    0x01a6: 'SH4',
    0x01a8: 'SH5',
    0x01c0: 'ARM',
    0x01c2: 'THUMB',
    0x01c4: 'ARMNT',
    0x01d3: 'AM33',
    0x01f0: 'POWERPC',
    0x01f1: 'POWERPCFP',
    0x0200: 'IA64',
    0x0266: 'MIPS16',
    0x0284: 'ALPHA64',
    # 0x0284: 'AXP64', # same
    0x0366: 'MIPSFPU',
    0x0466: 'MIPSFPU16',
    0x0520: 'TRICORE',
    0x0cef: 'CEF',
    0x0ebc: 'EBC',
    0x8664: 'AMD64',
    0x9041: 'M32R',
    0xc0ee: 'CEE',
}


def get_shared_library_arch(filename):
    with io.open(filename, 'rb') as fp:
        dos_headers = fp.read(64)
        _ = fp.read(4)

        magic, skip, offset = struct.unpack(str('2s58sl'), dos_headers)

        if magic != b'MZ':
            raise Exception('Not an executable')

        fp.seek(offset, io.SEEK_SET)
        pe_header = fp.read(6)

        sig, skip, machine = struct.unpack(str('2s2sH'), pe_header)

        if sig != b'PE':
            raise Exception('Not a PE executable')

        return machine_types.get(machine, 'UNKNOWN')


def get_arch(filename):
    this_platform = sys.platform
    if this_platform.startswith('win'):
        machine_type = get_shared_library_arch(filename)
        if machine_type == 'I386':
            return 32,
        elif machine_type in ('IA64', 'AMD64'):
            return 64,
        else:
            return ()
    elif this_platform not in ('linux2', 'linux3', 'linux', 'darwin'):
        raise OSError('')

    out = check_output(["file", filename], stderr=subprocess.STDOUT)
    out = out.decode('ascii')
    ret = []
    if this_platform.startswith('linux'):
        if '32-bit' in out:
            ret.append(32)
        if '64-bit' in out:
            ret.append(64)
    elif this_platform == 'darwin':
        if '(for architecture i386)' in out:
            ret.append(32)
        if '(for architecture x86_64)' in out:
            ret.append(64)

    return tuple(ret)
