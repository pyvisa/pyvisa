# -*- coding: utf-8 -*-
"""
    pyvisa
    ~~~~~~

    Python wrapper of National Instrument (NI) Virtual Instruments Software
    Architecture library (VISA).

    This file is part of PyVISA.

    :copyright: (c) 2014 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import
import os
import logging
import subprocess

import pkg_resources

logger = logging.getLogger('pyvisa')
logger.addHandler(logging.NullHandler)

__version__ = "unknown"
try:  # try to grab the commit version of our package
    __version__ = (subprocess.check_output(["git", "describe"],
                                           stderr=subprocess.STDOUT,
                                           cwd=os.path.dirname(os.path.abspath(__file__)))).strip()
except:  # on any error just try to grab the version that is installed on the system
    try:
        __version__ = pkg_resources.get_distribution('pyvisa').version
    except:
        pass  # we seem to have a local copy without any repository control or installed without setuptools
              # so the reported version will be __unknown__

import wrapper
from .visa import instrument, ResourceManager, Instrument, SerialInstrument, get_instruments_list
from .errors import *


from .library import read_user_settings
_user_lib = read_user_settings()

if _user_lib:
    from . import vpp43
    vpp43.visa_library.load_library(_user_lib)

