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
from ctypes.util import find_library

if os.name == 'nt':
    from ctypes import WINFUNCTYPE as FUNCTYPE, WinDLL as Library
else:
    from ctypes import CFUNCTYPE as FUNCTYPE, CDLL as Library


from . import types
from .functions import *


