#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    vpp43.py - VISA VPP-4.3.2 functions implementation
#
#    Copyright © 2005 Gregor Thalhammer <gth@users.sourceforge.net>,
#                     Torsten Bronger <bronger@physik.rwth-aachen.de>.
#
#    This file is part of pyvisa.
#
#    pyvisa is free software; you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    pyvisa is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with pyvisa; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

__version__ = "$Revision$"
# $Source$


VI_SPEC_VERSION = 0x00300000

from vpp43_types import *
from vpp43_constants import *
from visa_exceptions import *
import os


def check_status(status):
    """Check return values for errors."""
    if status < 0:
        raise VisaIOError, status
    else:
        return status


# load VISA library

class _Singleton(object):
    """Base class for singleton classes.  Taken from
    <http://www.python.org/2.2.3/descrintro.html>.
    """
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    def init(self, *args, **kwds):
        pass

class _VisaLibrary(_Singleton):
    def init(self):
	self.__lib = None
    def load_library(self, path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"):
	if os.name == 'nt':
	    self.__lib = windll.visa32
	elif os.name == 'posix':
	    self.__lib = cdll.LoadLibrary(path)
	else:
	    self.__lib = None
	    raise OSNotSupported, os.name
    def __call__(self):
	if self.__lib is None:
	    self.load_library()
	return self.__lib

visa_library = _VisaLibrary()

