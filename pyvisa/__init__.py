#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    __init__.py - PyVISA's package initialisation.
#
#    Copyright © 2005, 2006, 2007, 2008
#                Torsten Bronger <bronger@physik.rwth-aachen.de>,
#                Gregor Thalhammer <gth@users.sourceforge.net>.
#  
#    This file is part of PyVISA.
#  
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the MIT licence:
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

import ConfigParser, os, sys
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
