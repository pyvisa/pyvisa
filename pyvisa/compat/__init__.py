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
PYTHON3 = sys.version >= '3'

if PYTHON3:
    string_types = str

    def u(x):
        return x

    integer_types = (int, )

    input = input
else:
    string_types = basestring

    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    integer_types = (int, long)

    input = raw_input

if sys.version_info < (2, 7):
    try:
        # noinspection PyPackageRequirements
        import unittest2 as unittest
    except ImportError:
        raise Exception("Testing PyVISA in Python 2.6 requires package 'unittest2'")
else:
    import unittest

try:
    from collections import OrderedDict
except ImportError:
    from .ordereddict import OrderedDict

try:
    from logging import NullHandler
except ImportError:
    from .nullhandler import NullHandler

try:
    from subprocess import check_output
except ImportError:
    from .check_output import check_output


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, str('temporary_class'), (), {})
