#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from setuptools import setup
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)


def read(filename):
    with open(filename, 'rb') as f:
        return f.read().decode('utf8')


long_description = '\n\n'.join([read('README'),
                                read('AUTHORS'),
                                read('CHANGES')])

__doc__ = long_description

requirements = []
if sys.version_info < (3,):
    requirements.append('enum34')

setup(name='PyVISA',
      description='Python VISA bindings for GPIB, RS232, TCPIP and USB instruments',
      version='1.10.0.dev',
      long_description=long_description,
      author='Torsten Bronger, Gregor Thalhammer',
      author_email='bronger@physik.rwth-aachen.de',
      maintainer='Hernan E. Grecco',
      maintainer_email='hernan.grecco@gmail.com',
      url='https://github.com/pyvisa/pyvisa',
      test_suite='pyvisa.testsuite.testsuite',
      keywords='VISA GPIB USB serial RS232 measurement acquisition',
      license='MIT License',
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
      install_requires=requirements,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
      packages=['pyvisa', 'pyvisa.compat',
                'pyvisa.ctwrapper',
                'pyvisa.resources',
                'pyvisa.thirdparty',
                'pyvisa.testsuite'],
      platforms="Linux, Windows,Mac",
      entry_points={'console_scripts':
                    ['pyvisa-shell=visa:visa_shell',
                     'pyvisa-info=visa:visa_info']},
      py_modules=['visa'],
      use_2to3=False,
      zip_safe=False)
