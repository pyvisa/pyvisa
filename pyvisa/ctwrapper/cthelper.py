# -*- coding: utf-8 -*-
"""
    pyvisa.ctwrapper._ct
    ~~~~~~~~~~~~~~~~~~~~

    Cross platform helper of ctypes.

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import

# ctypes and os shouldn't be re-exported.
import os as _os
import sys as _sys

import ctypes as _ctypes

PYTHON3 = _sys.version_info >= (3, 0)

if _os.name == 'nt':
    FUNCTYPE, Library = _ctypes.WINFUNCTYPE, _ctypes.WinDLL
else:
    FUNCTYPE, Library = _ctypes.CFUNCTYPE, _ctypes.CDLL

# On Linux, find Library returns the name not the path.
# This excerpt provides a modified find_library.
# noinspection PyUnresolvedReferences
if _os.name == "posix" and _sys.platform.startswith('linux'):

    # Andreas Degert's find functions, using gcc, /sbin/ldconfig, objdump
    def define_find_libary():
        import re
        import tempfile
        import errno

        def _findlib_gcc(name):
            expr = r'[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
            fdout, ccout = tempfile.mkstemp()
            _os.close(fdout)
            cmd = 'if type gcc >/dev/null 2>&1; then CC=gcc; else CC=cc; fi;' \
                  '$CC -Wl,-t -o ' + ccout + ' 2>&1 -l' + name
            trace = ''
            try:
                f = _os.popen(cmd)
                trace = f.read()
                f.close()
            finally:
                try:
                    _os.unlink(ccout)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
            res = re.search(expr, trace)
            if not res:
                return None
            return res.group(0)

        def _findlib_ldconfig(name):
            # XXX assuming GLIBC's ldconfig (with option -p)
            expr = r'/[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
            with _os.popen('/sbin/ldconfig -p 2>/dev/null') as pipe:
                res = re.search(expr, pipe.read())
            if not res:
                # Hm, this works only for libs needed by the python executable.
                cmd = 'ldd %s 2>/dev/null' % _sys.executable
                with _os.popen(cmd) as pipe:
                    res = re.search(expr, pipe.read())
                if not res:
                    return None
            return res.group(0)

        def _find_library(name):
            path = _findlib_ldconfig(name) or _findlib_gcc(name)
            if path:
                return _os.path.realpath(path)
            return path

        return _find_library

    find_library = define_find_libary()
else:
    from ctypes.util import find_library
