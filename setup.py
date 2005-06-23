#!/usr/bin/env python

from distutils.core import setup

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
      py_modules = ['visa', 'pyvisa', 'vpp43', 'visa_messages',
		    'visa_attributes', 'vpp43_attributes', 'visa_exceptions',
		    'vpp43_types', 'vpp43_constants'])
