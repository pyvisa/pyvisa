#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    setup.py - Distutil setup script for PyVISA
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
#    pyvisa is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.	See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with pyvisa; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

from distutils.core import setup

def prune_tree(path):
    try:
	shutil.rmtree(path)
    except OSError:
	pass

prune_tree("build")

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(name = 'pyvisa',
      description = 'PyVISA, a python package to support the VISA I/O standard',
      version = '0.2',
      long_description = 'A Python package for support of the "Virtual '\
	  'Instrument Software Architecture" (VISA), in order to control '\
	  'measurement devices and test equipment via GPIB, RS232, or USB.',
      author = 'Gregor Thalhammer, Torsten Bronger',
      author_email = 'Gregor.Thalhammer@uibk.ac.at',
      maintainer_email = 'pyvisa-devel@lists.sourceforge.net',
      url = 'http://pyvisa.sourceforge.net',
      download_url = 'http://sourceforge.net/projects/pyvisa/',
      keywords = 'VISA GPIB USB serial RS232 measurement acquisition',
      classifiers = classifiers,
      package_dir = {'visa': 'src'},
      packages = ['visa'])
