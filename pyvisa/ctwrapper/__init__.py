# -*- coding: utf-8 -*-
"""
    pyvisa.wrapper
    ~~~~~~~~~~~~~~

    ctypes wrapper for VISA library.

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

import os
import sys

if os.name == 'nt':
    from ctypes import WINFUNCTYPE as FUNCTYPE, WinDLL as Library
else:
    from ctypes import CFUNCTYPE as FUNCTYPE, CDLL as Library


from . import types
from .functions import *


# On Linux, find Library returns the name not the path.
# This excerpt provides a modified find_library.
if os.name == "posix" and sys.platform.startswith('linux'):

    # Andreas Degert's find functions, using gcc, /sbin/ldconfig, objdump
    import re, tempfile, errno

    def _findLib_gcc(name):
        expr = r'[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
        fdout, ccout = tempfile.mkstemp()
        os.close(fdout)
        cmd = 'if type gcc >/dev/null 2>&1; then CC=gcc; else CC=cc; fi;' \
              '$CC -Wl,-t -o ' + ccout + ' 2>&1 -l' + name
        try:
            f = os.popen(cmd)
            trace = f.read()
            f.close()
        finally:
            try:
                os.unlink(ccout)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
        res = re.search(expr, trace)
        if not res:
            return None
        return res.group(0)

    def _findLib_ldconfig(name):
        # XXX assuming GLIBC's ldconfig (with option -p)
        expr = r'/[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
        res = re.search(expr,
                        os.popen('/sbin/ldconfig -p 2>/dev/null').read())
        if not res:
            # Hm, this works only for libs needed by the python executable.
            cmd = 'ldd %s 2>/dev/null' % sys.executable
            res = re.search(expr, os.popen(cmd).read())
            if not res:
                return None
        return res.group(0)

    def find_library(name):
        path = _findLib_ldconfig(name) or _findLib_gcc(name)
        if path:
            return os.path.realpath(path)
        return path

else:
    from ctypes.util import find_library
