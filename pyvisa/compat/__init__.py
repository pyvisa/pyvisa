# -*- coding: utf-8 -*-
"""
    pyvisa.compat
    ~~~~~~~~~~~~~

    Compatibility layer.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import
import sys
import unittest

from subprocess import check_output


PYTHON3 = sys.version >= '3'

if PYTHON3:
    string_types = str

    def u(x):
        return x

    integer_types = (int, )

    input = input

    int_to_bytes = int.to_bytes
else:
    string_types = basestring

    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    integer_types = (int, long)

    input = raw_input

    # Implementation extracted from the python-future project

    def int_to_bytes(integer, length, byteorder='big', signed=False):
        """
        Return an array of bytes representing an integer.
        The integer is represented using length bytes.  An OverflowError is
        raised if the integer is not representable with the given number of
        bytes.
        The byteorder argument determines the byte order used to represent the
        integer.  If byteorder is 'big', the most significant byte is at the
        beginning of the byte array.  If byteorder is 'little', the most
        significant byte is at the end of the byte array.  To request the
        native byte order of the host system, use `sys.byteorder' as the byte
        order value.
        The signed keyword-only argument determines whether two's complement is
        used to represent the integer.  If signed is False and a negative
        integer is given, an OverflowError is raised.
        """
        if length < 0:
            raise ValueError("length argument must be non-negative")
        if length == 0 and integer == 0:
            return bytes()
        if signed and integer < 0:
            bits = length * 8
            num = (2**bits) + integer
            if num <= 0:
                raise OverflowError("int too smal to convert")
        else:
            if integer < 0:
                raise OverflowError("can't convert negative int to unsigned")
            num = integer
        if byteorder not in ('little', 'big'):
            raise ValueError("byteorder must be either 'little' or 'big'")
        h = b'%x' % num
        s = bytes((b'0'*(len(h) % 2) + h).zfill(length*2).decode('hex'))
        if signed:
            high_set = s[0] & 0x80
            if integer > 0 and high_set:
                raise OverflowError("int too big to convert")
            if integer < 0 and not high_set:
                raise OverflowError("int too small to convert")
        if len(s) > length:
            raise OverflowError("int too big to convert")
        return s if byteorder == 'big' else s[::-1]

if sys.version_info < (2, 7):
    try:
        # noinspection PyPackageRequirements
        import unittest2 as unittest
    except ImportError:
        raise Exception("Testing PyVISA in Python 2.6 requires package 'unittest2'")

    import struct

    def int_from_bytes(data, byteorder):
        if byteorder not in ('little', 'big'):
            raise ValueError("byteorder must be either 'little' or 'big'")
        data_format = '>i' if byteorder == 'big' else '<i'
        return struct.unpack(data_format, data)[0]
else:
    import unittest
    int_from_bytes = int.from_bytes

try:
    from collections import OrderedDict
except ImportError:
    from .ordereddict import OrderedDict

try:
    from logging import NullHandler
except ImportError:
    from .nullhandler import NullHandler


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, str('temporary_class'), (), {})
