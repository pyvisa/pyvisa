# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals, print_function, absolute_import

from pyvisa.testsuite import BaseTestCase

from pyvisa import util

try:
    # noinspection PyPackageRequirements
    import numpy as np
except ImportError:
    np = None

class TestParser(BaseTestCase):

    def test_parse_binary(self):
        s = b'#A@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xde\x8b<@\xde\x8b<@\xde\x8b<' \
            b'@\xde\x8b<@\xe0\x8b<@\xe0\x8b<@\xdc\x8b<@\xde\x8b<@\xe2\x8b<@\xe0\x8b<'
        e = [0.01707566, 0.01707566, 0.01707566, 0.01707566, 0.01707375,
             0.01707375, 0.01707375, 0.01707375, 0.01707470, 0.01707470,
             0.01707280, 0.01707375, 0.01707566, 0.01707470]
        p = util.parse_binary(s, is_big_endian=False, is_single=True)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)
        p = util.from_ieee_block(s, datatype='f', is_big_endian=False)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)

    def test_ieee_integer(self):
        values = list(range(99))
        containers = (list, tuple) #+ ((np.asarray,) if np else ())
        for fmt in 'bBhHiIfd':
            for endi in (True, False):
                for cont in containers:
                    conv = cont(values)
                    msg = 'fmt=%s, endianness=%s, container=%s' % (fmt, endi, cont.__name__)
                    try:
                        block = util.to_ieee_block(conv, fmt, endi)
                        parsed = util.from_ieee_block(block, fmt, endi, cont)
                    except Exception as e:
                        raise Exception(msg + '\n' + repr(e))

                    self.assertEqual(conv, parsed, msg)

    def test_ieee_noninteger(self):
        values = [val + 0.5 for val in range(99)]
        containers = (list, tuple) #+ ((np.asarray,) if np else ())
        for fmt in 'fd':
            for endi in (True, False):
                for cont in containers:
                    conv = cont(values)
                    msg = 'fmt=%s, endianness=%s, container=%s' % (fmt, endi, cont.__name__)
                    try:
                        block = util.to_ieee_block(conv, fmt, endi)
                        parsed = util.from_ieee_block(block, fmt, endi, cont)
                    except Exception as e:
                        raise Exception(msg + '\n' + repr(e))

                    self.assertEqual(conv, parsed, msg)
