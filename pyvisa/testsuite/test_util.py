# -*- coding: utf-8 -*-
"""Test pyvisa utility functions.

"""
from pyvisa.testsuite import BaseTestCase

from pyvisa import util

try:
    # noinspection PyPackageRequirements
    import numpy as np
except ImportError:
    np = None


# XXX test reading config from file (use tempfile)

class TestParser(BaseTestCase):

    def test_parse_binary(self):
        s = (b'#A@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xde\x8b<@\xde\x8b<@'
             b'\xde\x8b<@\xde\x8b<@\xe0\x8b<@\xe0\x8b<@\xdc\x8b<@\xde\x8b<@'
             b'\xe2\x8b<@\xe0\x8b<')
        e = [0.01707566, 0.01707566, 0.01707566, 0.01707566, 0.01707375,
             0.01707375, 0.01707375, 0.01707375, 0.01707470, 0.01707470,
             0.01707280, 0.01707375, 0.01707566, 0.01707470]

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

    def test_invalid_string_converter(self):
        with self.raises(ValueError) as ex:
            util.to_ascii_block([1,2], 'm')
        self.assertIn("unsupported format character", ex.value)
        with self.raises(ValueError) as ex:
            util.from_ascii_block("1,2,3", 'm')
        self.assertIn("Invalid code for converter", ex.value)

    def test_function_separator(self):
        values = list(range(99))
        fmt = "d"
        msg = 'block=ascii, fmt=%s' % fmt
        tb = lambda values: util.to_ascii_block(values, fmt, ':'.join)
        fb = lambda block, cont: util.from_ascii_block(block, fmt, ':'.split,
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

    def test_malformed_binary_block_header(self):
        values = list(range(99))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            bad_block = block[1:]
            with self.assertRaises(ValueError) as e:
                fb(bad_block, "h", False, list)

            self.assertIn("(#", e.exception.args[0])

    def test_binary_block_shorter_than_advertized(self):
        values = list(range(99))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            if header == "ieee":
                l = int(block[1])
                block = block[:2] + b"9" * l + block[2+l:]
            else:
                block = block[:2] + b"\xff\xff\xff\xff" * l + block[2+l:]
            with self.assertRaises(ValueError) as e:
                fb(block, "h", False, list)

            self.assertIn("Binary data is incomplete", e.exception.args[0])

    def test_guessing_block_length(self):
        values = list(range(99))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            if header == "ieee":
                l = int(block[1])
                block[2:2+l] = int("0" * l)
            else:
                block[2:2+4] = "\x00\x00\x00\x00"
            self.assertListEqual(fb(block, "h", False, list),
                                 values)

    # XXX malformed binary
    def test_handling_malformed_binary(self):
        pass

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

# XXX system details and binary analysis
