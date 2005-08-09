#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    test_keithley2000.py - PyVISA test code for Keithley 2000 multimeter
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
keithley = GpibInstrument(12)
milliseconds = 500
number_of_values = 10
keithley.write("F0B2M2G0T2Q%dI%dX" % (milliseconds, number_of_values))
keithley.trigger()
keithley.wait_for_srq()
voltages = keithley.read_floats()
print "Average: ", sum(voltages) / len(voltages)
print "Test end"
