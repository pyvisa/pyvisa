# -*- coding: utf-8 -*-
"""
    pyvisa.compat.struct
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Python 2/3 compatibility for struct module

    :copyright: 2015, PSF
    :license: PSF License
"""

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import sys
import struct

# we always want the exception to be able to catch it
error = struct.error

# compatibility for unicode literals was introduced in 2.7.8
# if we're above that there is nothing to do except aliasing
if sys.hexversion >= 0x02070800:
    pack = struct.pack
    pack_into = struct.pack_into
    unpack = struct.unpack
    unpack_from = struct.unpack_from
    calcsize = struct.calcsize
else:
    def pack(fmt, *args):
        return struct.pack(str(fmt), *args)

    def pack_into(fmt, *args, **argk):
        return struct.pack_into(str(fmt), *args, **argk)

    def unpack(fmt, string):
        return struct.unpack(str(fmt), string)

    def unpack_from(fmt, *args, **kwargs):
        return struct.unpack_from(str(fmt), *args, **kwargs)

    def calcsize(fmt):
        return struct.calcsize(str(fmt))
