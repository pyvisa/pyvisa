# -*- coding: utf-8 -*-

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from pyvisa.testsuite import BaseTestCase

from pyvisa import util

try:
    # noinspection PyPackageRequirements
    import numpy as np
except ImportError:
    np = None


class TestParser(BaseTestCase):

    def test_parse_binary(self):
        s = (b'#A@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xde\x8b<@\xde\x8b<@'
             b'\xde\x8b<@\xde\x8b<@\xe0\x8b<@\xe0\x8b<@\xdc\x8b<@\xde\x8b<@'
             b'\xe2\x8b<@\xe0\x8b<')
        e = [0.01707566, 0.01707566, 0.01707566, 0.01707566, 0.01707375,
             0.01707375, 0.01707375, 0.01707375, 0.01707470, 0.01707470,
             0.01707280, 0.01707375, 0.01707566, 0.01707470]
        with self.assertWarns(FutureWarning):
            p = util.parse_binary(s, is_big_endian=False, is_single=True)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)

        # Test handling indefinite length block
        p = util.from_ieee_block(s, datatype='f', is_big_endian=False)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)

        # Test handling definite length block
        p = util.from_ieee_block(b'#214' + s[2:], datatype='f',
                                 is_big_endian=False)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)

        p = util.from_hp_block(b'#A\x0e\x00' + s[2:], datatype='f',
                               is_big_endian=False)
        for a, b in zip(p, e):
            self.assertAlmostEqual(a, b)

    def test_integer_ascii_block(self):
        values = list(range(99))
        for fmt in 'd':
            msg = 'block=%s, fmt=%s'
            msg = msg % ('ascii', fmt)
            tb = lambda values: util.to_ascii_block(values, fmt, ',')
            fb = lambda block, cont: util.from_ascii_block(block, fmt, ',',
                                                           cont)
            self.round_trip_block_converstion(values, tb, fb, msg)

    def test_non_integer_ascii_block(self):
        values = [val + 0.5 for val in range(99)]
        values = list(range(99))
        for fmt in 'fFeEgG':
            msg = 'block=%s, fmt=%s'
            msg = msg % ('ascii', fmt)
            tb = lambda values: util.to_ascii_block(values, fmt, ',')
            fb = lambda block, cont: util.from_ascii_block(block, fmt, ',',
                                                           cont)
            self.round_trip_block_converstion(values, tb, fb, msg)

    def test_integer_binary_block(self):
        values = list(range(99))
        for block, tb, fb in zip(('ieee', 'hp'),
                                 (util.to_ieee_block, util.to_hp_block),
                                 (util.from_ieee_block, util.from_hp_block)):
            for fmt in 'bBhHiIfd':
                for endi in (True, False):
                    msg = 'block=%s, fmt=%s, endianness=%s'
                    msg = msg % (block, fmt, endi)
                    tblock = lambda values: tb(values, fmt, endi)
                    fblock = lambda block, cont: fb(block, fmt, endi, cont)
                    self.round_trip_block_converstion(values, tblock, fblock,
                                                      msg)

    def test_noninteger_binary_block(self):
        values = [val + 0.5 for val in range(99)]
        for block, tb, fb in zip(('ieee', 'hp'),
                                 (util.to_ieee_block, util.to_hp_block),
                                 (util.from_ieee_block, util.from_hp_block)):
            for fmt in 'fd':
                for endi in (True, False):
                    msg = 'block=%s, fmt=%s, endianness=%s'
                    msg = msg % (block, fmt, endi)
                    tblock = lambda values: bytearray(tb(values, fmt, endi))
                    fblock = lambda block, cont: fb(block, fmt, endi, cont)
                    self.round_trip_block_converstion(values, tblock, fblock,
                                                      msg)

    def round_trip_block_converstion(self, values, to_block, from_block, msg):
        """Test that block conversion round trip as expected.

        """
        containers = (list, tuple) + ((np.array,) if np else ())
        for cont in containers:
            conv = cont(values)
            msg += ', container=%s'
            msg = msg % cont.__name__
            try:
                block = to_block(conv)
                parsed = from_block(block, cont)
            except Exception as e:
                raise Exception(msg + '\n' + repr(e))

            if np and cont in (np.array,):
                np.testing.assert_array_equal(conv, parsed, msg)
            else:
                self.assertEqual(conv, parsed, msg)
