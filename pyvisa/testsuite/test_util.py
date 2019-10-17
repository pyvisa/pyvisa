# -*- coding: utf-8 -*-
"""Test pyvisa utility functions.

"""
import array
import contextlib
import os
import sys
import tempfile
from configparser import ConfigParser
from io import StringIO
from functools import partial

from pyvisa import util
from pyvisa.testsuite import BaseTestCase

try:
    # noinspection PyPackageRequirements
    import numpy as np
except ImportError:
    np = None


class TestConfigFile(BaseTestCase):
    """Test reading information from a user configuration file.

    """

    def setUp(self):
        # Skip if a real config file exists
        if any(os.path.isfile(p)
               for p in [os.path.join(sys.prefix, "share", "pyvisa", ".pyvisarc"),
                         os.path.join(os.path.expanduser("~"), ".pyvisarc")]
              ):
            self.skipTest(".pyvisarc file exists cannot properly test in this case")
        self.temp_dir = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.temp_dir.name, "share", "pyvisa"))
        self.config_path = os.path.join(self.temp_dir.name, "share", "pyvisa",
                                        ".pyvisarc")
        self._prefix = sys.prefix
        sys.prefix = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()
        sys.prefix = self._prefix

    def test_reading_config_file(self):
        config = ConfigParser()
        config['Paths'] = {}
        config['Paths']["visa library"] = "test"
        with open(self.config_path, "w") as f:
            config.write(f)
        self.assertEqual(util.read_user_library_path(), "test")

    def test_no_section(self):
        config = ConfigParser()
        with open(self.config_path, "w") as f:
            config.write(f)
        with self.assertLogs(level='DEBUG') as cm:
            self.assertIsNone(util.read_user_library_path())
        self.assertIn("NoOptionError or NoSectionError", cm.output[1])

    def test_no_key(self):
        config = ConfigParser()
        config['Paths'] = {}
        with open(self.config_path, "w") as f:
            config.write(f)
        with self.assertLogs(level='DEBUG') as cm:
            self.assertIsNone(util.read_user_library_path())
        self.assertIn("NoOptionError or NoSectionError", cm.output[1])

    def test_no_config_file(self):
        with self.assertLogs(level='DEBUG') as cm:
            self.assertIsNone(util.read_user_library_path())
        self.assertIn("No user defined", cm.output[0])

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
                               is_big_endian=False,
                               container=partial(array.array, 'f'))
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
        with self.assertRaises(ValueError) as ex:
            util.to_ascii_block([1,2], 'm')
        self.assertIn("unsupported format character", ex.exception.args[0])
        with self.assertRaises(ValueError) as ex:
            util.from_ascii_block("1,2,3", 'm')
        self.assertIn("Invalid code for converter", ex.exception.args[0])

    def test_function_separator(self):
        values = list(range(99))
        fmt = "d"
        msg = 'block=ascii, fmt=%s' % fmt
        tb = lambda values: util.to_ascii_block(values, fmt, ':'.join)
        fb = lambda block, cont: util.from_ascii_block(
            block, fmt, lambda s: s.split(':'), cont)
        self.round_trip_block_converstion(values, tb, fb, msg)

    def test_function_converter(self):
        values = list(range(99))
        msg = 'block=ascii'
        tb = lambda values: util.to_ascii_block(values, str, ':'.join)
        fb = lambda block, cont: util.from_ascii_block(
            block, int, lambda s: s.split(':'), cont)
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
        values = list(range(10))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            bad_block = block[1:]
            with self.assertRaises(ValueError) as e:
                fb(bad_block, "h", False, list)

            self.assertIn("(#", e.exception.args[0])

    def test_weird_binary_block_header(self):
        values = list(range(100))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            bad_block = block[1:]
            if header == 'hp':
                index = bad_block.find(b'#')
                bad_block = bad_block[:index] + b"#A" + bad_block[index+2:]
            with self.assertWarns(UserWarning):
                fb(bad_block, "h", False, list)

    def test_weird_binary_block_header_raise(self):
        values = list(range(100))
        for header, tb, fb in zip(('ieee', 'hp'),
                                  (util.to_ieee_block, util.to_hp_block),
                                  (util.from_ieee_block, util.from_hp_block)):
            block = tb(values, "h", False)
            bad_block = block[1:]
            if header == 'hp':
                index = bad_block.find(b'#')
                bad_block = bad_block[:index] + b"#A" + bad_block[index+2:]
            parse = (util.parse_ieee_block_header if header == 'ieee' else
                     partial(util.parse_hp_block_header, is_big_endian=False))

            with self.assertRaises(RuntimeError):
                parse(bad_block, raise_on_late_block=True)

            parse(bad_block, length_before_block=1000)

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
            block = tb(values, "h", False) + b"\n"
            if header == "ieee":
                l = int(block[1:2].decode())
                block = block[:2] + b"0" * l + block[2+l:]
            else:
                block = block[:2] + b"\x00\x00\x00\x00" + block[2+4:]
            self.assertListEqual(fb(block, "h", False, list),
                                 values)

    def test_handling_malformed_binary(self):
        containers = (list, tuple) + ((np.array, np.ndarray) if np else ())

        # Use this to generate malformed data which should in theory be
        # impossible
        class DumbBytes(bytes):
            def __len__(self):
                return 10

        for container in containers:
            with self.assertRaises(ValueError) as e:
                util.from_binary_block(DumbBytes(b"\x00\x00\x00"),
                                       container=container)
            self.assertIn("malformed" if container in (list, tuple) else "buffer",
                          e.exception.args[0])

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


class TestSystemDetailsAnalysis(BaseTestCase):
    """Test geeting the system details.

    """

    def test_getting_system_details(self):
        details = util.get_system_details(False)
        self.assertFalse(details['backends'])

    def test_get_debug_info(self):
        details = util.system_details_to_str(util.get_system_details())
        self.assertSequenceEqual(util.get_debug_info(False), details)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            util.get_debug_info()
        output = temp_stdout.getvalue()
        self.assertSequenceEqual(output.strip(), details.strip())
