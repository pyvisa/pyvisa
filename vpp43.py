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

"""Main module of the implementation of the original VISA routines.

See VPP-4.3.2.

"""

__version__ = "$Revision$"
# $Source$


VI_SPEC_VERSION = 0x00300000

from vpp43_types import *
from vpp43_constants import *
from visa_exceptions import *
import os


# load VISA library

class _Singleton(object):
    """Base class for singleton classes.

    Taken from <http://www.python.org/2.2.3/descrintro.html>.

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
    """Singleton class for VISA ctypes library handle.

    This class has only one instance called "visa_library".  The purpose of its
    instance is to provide access to the ctypes object that contains the VISA
    library.

    Public methods:
    load_library -- (re-)loads the VISA library
    __call__     -- returns the ctypes object holding the VISA library
    """
    def init(self):
	self.__lib = None
    def load_library(self, path = "/usr/local/vxipnp/linux/bin/libvisa.so.7"):
	"""(Re-)loads the VISA library.

	The optional parameter "path" holds the full path to the VISA library.
	At the moment, it has significance only for Linux.  It is called
	implicitly by __call__ if not called successfully before.

	It may raise an OSNotSupported exception, or an OSError if the library
	file was not found.

	"""
	if os.name == 'nt':
	    self.__lib = windll.visa32
	elif os.name == 'posix':
	    self.__lib = cdll.LoadLibrary(path)
	else:
	    self.__lib = None
	    raise OSNotSupported, os.name
    def __call__(self):
	"""Returns the ctypes object to the VISA library."""
	if self.__lib is None:
	    self.load_library()
	return self.__lib

visa_library = _VisaLibrary()


def check_status(status):
    """Check return values for errors."""
    if status < 0:
        raise VisaIOError, status
    else:
        return status

