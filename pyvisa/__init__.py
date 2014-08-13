# -*- coding: utf-8 -*-
"""
    pyvisa
    ~~~~~~

    Python wrapper of National Instrument (NI) Virtual Instruments Software
    Architecture library (VISA).

    This file is part of PyVISA.

    :copyright: 2014 by PyVISA Authors, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division, unicode_literals, print_function, absolute_import
import os
import logging
import subprocess

import pkg_resources

from . import compat
logger = logging.getLogger('pyvisa')
logger.addHandler(compat.NullHandler())


def log_to_screen(level=logging.DEBUG):
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)

    logger.addHandler(ch)


__version__ = "unknown"
try:                # pragma: no cover
    __version__ = pkg_resources.get_distribution('pyvisa').version
except:             # pragma: no cover
    pass  # we seem to have a local copy without any repository control or installed without setuptools
          # so the reported version will be __unknown__

from . import ctwrapper
from .errors import *
