#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    __init__.py - PyVISA's package initialisation.
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#		      Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of PyVISA.
#
#    PyVISA is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    PyVISA is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.	See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with PyVISA; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import ConfigParser, os, sys
import vpp43

_config_parser = ConfigParser.SafeConfigParser()
_config_parser.read([os.path.join(sys.prefix, "share", "pyvisa", ".pyvisarc"),
		     os.path.join(os.path.expanduser("~"), ".pyvisarc")])
try:
    visa_library_path = _config_parser.get("Paths", "visa library")
except ConfigParser.Error:
    pass
else:
    vpp43.visa_library.load_library(visa_library_path)
