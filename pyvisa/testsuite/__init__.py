# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function, absolute_import

import os
import unittest

def testsuite():
    """A testsuite that has all the pyflim tests.
    """
    return unittest.TestLoader().discover(os.path.dirname(__file__))


def main():
    """Runs the testsuite as command line application."""
    try:
        unittest.main()
    except Exception as e:
        print('Error: %s' % e)
