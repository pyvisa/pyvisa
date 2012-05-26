# -*- coding: utf-8 -*-
"""
    pyvisa
    ~~~~~~

    Python wrapper of National Instrument (NI) Virtual Instruments Software
    Architecture library (VISA).

    This file is part of PyVISA.

    :copyright: (c) 2012 by the PyVISA authors.
    :license: MIT, see COPYING for more details.
"""

import os
import sys
import ConfigParser
import vpp43

_config_parser = ConfigParser.SafeConfigParser()
_config_parser.read([os.path.join(sys.prefix, "share", "pyvisa", ".pyvisarc"),
                     os.path.join(os.path.expanduser("~"), ".pyvisarc")])
try:
    _visa_library_path = _config_parser.get("Paths", "visa library")
except ConfigParser.Error:
    pass
else:
    vpp43.visa_library.load_library(_visa_library_path)
