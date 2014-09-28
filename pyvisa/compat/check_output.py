# -*- coding: utf-8 -*-
"""
    pyvisa.compat.check_output
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Taken from the Python 2.7 source code.

    :copyright: 2013, PSF
    :license: PSF License
"""

from __future__ import division, unicode_literals, print_function, absolute_import

import subprocess


def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    Backported from Python 2.7 as it's implemented as pure python on stdlib.

    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output
