#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import sys
    reload(sys).setdefaultencoding("UTF-8")
except:
    pass


try:
    from setuptools import setup
except ImportError:
    print('Please install or upgrade setuptools or pip to continue')
    sys.exit(1)


import codecs


def read(filename):
    return codecs.open(filename, encoding='utf-8').read()


long_description = '\n\n'.join([read('README'),
                                read('AUTHORS'),
                                read('CHANGES')])

__doc__ = long_description

requirements = []
if sys.version_info < (3, 4):
    requirements.append('enum34')

if sys.version_info < (2, 7):
    requirements.append('unittest2')

setup(name='PyVISA',
      description='Python VISA bindings for GPIB, RS232, and USB instruments',
      version='1.6.3',
      long_description=long_description,
      author='Torsten Bronger, Gregor Thalhammer',
      author_email='bronger@physik.rwth-aachen.de',
      maintainer='Hernan E. Grecco',
      maintainer_email='hernan.grecco@gmail.com',
      url='https://github.com/hgrecco/pyvisa',
      test_suite='pyvisa.testsuite.testsuite',
      keywords='VISA GPIB USB serial RS232 measurement acquisition',
      license='MIT License',
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
      packages=['pyvisa', 'pyvisa.compat',
                'pyvisa.ctwrapper',
                'pyvisa.resources',
                'pyvisa.thirdparty',
                'pyvisa.testsuite'],
      platforms="Linux, Windows,Mac",
      py_modules=['visa'],
      use_2to3=False,
      zip_safe=False)
