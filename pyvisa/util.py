# -*- coding: utf-8 -*-
"""
    pyvisa.util
    ~~~~~~~~~~~

    General utility functions.

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import io
import os
import re
import sys
import struct
import subprocess
from .compat import check_output
import contextlib
import platform
import warnings

from . import __version__

if sys.version >= '3':
    _struct_unpack = struct.unpack
else:
    def _struct_unpack(fmt, string):
        return struct.unpack(str(fmt), string)


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
        from ConfigParser import SafeConfigParser as ConfigParser, NoSectionError
    except ImportError:
        from configparser import ConfigParser, NoSectionError

    config_parser = ConfigParser()
    config_parser.read([os.path.join(sys.prefix, "share", "pyvisa", ".pyvisarc"),
                        os.path.join(os.path.expanduser("~"), ".pyvisarc")])

    try:
        return config_parser.get("Paths", "visa library")
    except (KeyError, NoSectionError):
        return None


class LibraryPath(str):

    def __new__(cls, path, found_by='auto'):
        obj = super(LibraryPath, cls).__new__(cls, path)
        obj.path = path
        obj.found_by = found_by

        obj._arch = None

        return obj

    @property
    def arch(self):
        if self._arch is None:
            try:
                self._arch = get_arch(self.path)
            except Exception as e:
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


def get_library_paths(wrapper_module):
    """Return a tuple of possible library paths.

    These paths are tried when `VisaLibrary` is instantiated without arguments.

    :param wrapper_module: the python module/package that wraps the visa library.
    """
    user_lib = read_user_library_path()
    tmp = [wrapper_module.find_library(library_path)
           for library_path in ('visa', 'visa32', 'visa32.dll')]

    tmp = [LibraryPath(library_path)
           for library_path in tmp
           if library_path is not None]

    if user_lib:
        user_lib = LibraryPath(user_lib, 'user')
        try:
            tmp.remove(user_lib)
        except ValueError:
            pass
        tmp.insert(0, user_lib)

    return tuple(tmp)


def removefilter(action, message="", category=Warning, module="", lineno=0,
                 append=0):
    """Remove all entries from the list of warnings filters that match the
    given filter.

    It is the opposite to warnings.filterwarnings() and has the same parameters
    as it."""
    import re
    item = (action, re.compile(message, re.I), category, re.compile(module), lineno)

    new_filters = [fil for fil in warnings.filters if fil != item]

    if len(warnings.filters) == len(new_filters):
        warnings.warn("Warning filter not found", stacklevel=2)

    warnings.filters = new_filters


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


@contextlib.contextmanager
def warning_context(action, message="", category=Warning, module="", lineno=0, append=False):
    warnings.filterwarnings(action, message, category, module, lineno, append)
    yield
    removefilter(action, message, category, module, lineno, append)


_ascii_re = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\d*\.\d+)(?:[eE][-+]?\d+)?")


def parse_ascii(bytes_data):
    return [float(raw_value) for raw_value in
            _ascii_re.findall(bytes_data.decode('ascii'))]


def parse_binary(bytes_data, is_big_endian=False, is_single=False):

    data = bytes_data

    hash_sign_position = bytes_data.find(b"#")
    if hash_sign_position == -1 or len(data) - hash_sign_position < 3:
        raise ValueError('Cound not find valid hash position')

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
    elif data_1 == "0" and data[-1:].decode('ascii') == "\n":
        data = data[2:-1]
        data_length = len(data)
    else:
        raise ValueError()

    if is_big_endian:
        endianess = ">"
    else:
        endianess = "<"

    try:
        if is_single:
            result = list(_struct_unpack((endianess +
                                         str(data_length // 4) + "f").encode('ascii'), data))
        else:
            result = list(_struct_unpack(endianess +
                                        str(data_length // 8) + "d", data))
    except struct.error:
        raise ValueError("Binary data itself was malformed")

    return result


def get_system_details(visa=True):
    """Return a dictionary with information about the system
    """
    buildno, builddate = platform.python_build()
    python = platform.python_version()
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
                                  lambda:'n/a')(),
        'python': platform.python_version(),
        'compiler': platform.python_compiler(),
        'buildno': buildno,
        'builddate': builddate,
        'unicode': unitype,
        'bits': bits,
        'pyvisa': __version__
        }

    if visa:
        from . import ctwrapper
        d['visa'] = get_library_paths(ctwrapper)
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
         'VISA:',
         '   PyVISA Version: %s' % d.get('pyvisa', 'n/a'),
         '',
         ]

    for ndx, visalib in enumerate(d.get('visa', ()), 1):
        l.append('   #%d: %s' % (ndx, visalib))
        l.append('      found by: %s' % visalib.found_by)
        l.append('      bitness: %s' % visalib.bitness)

    if not d.get('visa', ()):
        l.append('   Not found.')

    joiner = '\n' + indent
    print(indent + joiner.join(l) + '\n')


def get_debug_info():
    return system_details_to_str(get_system_details())


def pip_install(package):
    try:
        import pip
    except ImportError:
        print(system_details_to_str(get_system_details()))
        raise RuntimeError('Please install pip to continue.')

    return pip.main(['install', package])

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
    0x0284: 'AXP64', # same
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

        magic, skip, offset = _struct_unpack(str('2s58sl'), dos_headers)

        if magic != b'MZ':
            raise Exception('Not an executable')

        fp.seek(offset, io.SEEK_SET)
        pe_header = fp.read(6)

        sig, skip, machine = _struct_unpack(str('2s2sH'), pe_header)

        if sig != b'PE':
            raise Exception('Not a PE executable')

        return machine_types.get(machine, 'UNKNOWN')


def get_arch(filename):
    platform = sys.platform
    if platform.startswith('win'):
        machine_type = get_shared_library_arch(filename)
        if machine_type == 'I386':
            return (32, )
        elif machine_type in ('IA64', 'AMD64'):
            return (64, )
        else:
            return ()
    elif not platform in ('linux2', 'linux3', 'linux', 'darwin'):
        raise OSError('')

    out = check_output(["file", filename], stderr=subprocess.STDOUT)
    out = out.decode('ascii')
    ret = []
    if platform.startswith('linux'):
        if '32-bit' in out:
            ret.append(32)
        if '64-bit' in out:
            ret.append(64)
    elif platform == 'darwin':
        if '(for architecture i386)' in out:
            ret.append(32)
        if '(for architecture x86_64)' in out:
            ret.append(64)

    return tuple(ret)
