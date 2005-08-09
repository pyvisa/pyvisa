#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    test_itc4.py - PyVISA test code for Oxfort ITC4 temperature controller
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#                     Torsten Bronger <bronger@physik.rwth-aachen.de>.
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
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with PyVISA; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from visa import *

print "Test start"
itc4 = Instrument("COM2", term_chars = "\r", timeout = 5)
itc4.write("V")
print itc4.read()
print "Test end"
