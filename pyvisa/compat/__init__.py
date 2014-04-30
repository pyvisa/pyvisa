# -*- coding: utf-8 -*-
"""
    pint.compat
    ~~~~~~~~~~~

    Compatibility layer.

    :copyright: 2013 by Pint Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import sys
PYTHON3 = sys.version >= '3'

if PYTHON3:
    string_types = str

    def u(x):
        return x
else:
    string_types = basestring

    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

try:
    from logging import NullHandler
except ImportError:
    from .nullhandler import NullHandler

try:
    from subprocess import check_output
except ImportError:
    from .check_output import check_output

