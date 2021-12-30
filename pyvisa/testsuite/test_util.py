# -*- coding: utf-8 -*-
"""Test pyvisa utility functions.

"""
import array
import contextlib
import logging
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from configparser import ConfigParser
from functools import partial
from io import StringIO
from types import ModuleType
from typing import Optional

import pytest

from pyvisa import highlevel, util
from pyvisa.ctwrapper import IVIVisaLibrary
from pyvisa.testsuite import BaseTestCase

np: Optional[ModuleType]
try:
    import numpy

    np = numpy
except ImportError:
    np = None


class TestConfigFile(BaseTestCase):
    """Test reading information from a user configuration file."""

    def setup_method(self):
        # Skip if a real config file exists
        if any(
            os.path.isfile(p)
            for p in [
                os.path.join(sys.prefix, "share", "pyvisa", ".pyvisarc"),
                os.path.join(os.path.expanduser("~"), ".pyvisarc"),
            ]
        ):
            raise unittest.SkipTest(
                ".pyvisarc file exists cannot properly test in this case"
            )
        self.temp_dir = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.temp_dir.name, "share", "pyvisa"))
        self.config_path = os.path.join(
            self.temp_dir.name, "share", "pyvisa", ".pyvisarc"
        )
        self._prefix = sys.prefix
        sys.prefix = self.temp_dir.name
        self._platform = sys.platform
        self._version_info = sys.version_info

    def teardown_method(self):
        self.temp_dir.cleanup()
        sys.prefix = self._prefix
        sys.platform = self._platform
        sys.version_info = self._version_info

    def test_reading_config_file(self):
        config = ConfigParser()
        config["Paths"] = {}
        config["Paths"]["visa library"] = "test"
        with open(self.config_path, "w") as f:
            config.write(f)
        assert util.read_user_library_path() == "test"

    def test_no_section(self, caplog):
        config = ConfigParser()
        with open(self.config_path, "w") as f:
            config.write(f)
        with caplog.at_level(level=logging.DEBUG):
            assert util.read_user_library_path() is None
        assert "NoOptionError or NoSectionError" in caplog.records[1].message

    def test_no_key(self, caplog):
        config = ConfigParser()
        config["Paths"] = {}
        with open(self.config_path, "w") as f:
            config.write(f)
        with caplog.at_level(level=logging.DEBUG):
            assert util.read_user_library_path() is None
        assert "NoOptionError or NoSectionError" in caplog.records[1].message

    def test_no_config_file(self, caplog):
        with caplog.at_level(level=logging.DEBUG):
            assert util.read_user_library_path() is None
        assert "No user defined" in caplog.records[0].message

    # --- Test reading dll_extra_paths.

    def test_reading_config_file_not_windows(self, caplog):
        sys.platform = "darwin"
        sys.version_info = (3, 8, 1)
        with caplog.at_level(level=logging.DEBUG):
            assert util.add_user_dll_extra_paths() is None
        assert "Not loading dll_extra_paths" in caplog.records[0].message

    def test_reading_config_file_old_python(self, caplog):
        sys.platform = "win32"
        sys.version_info = (3, 7, 1)
        with caplog.at_level(level=logging.DEBUG):
            assert util.add_user_dll_extra_paths() is None
        assert "Not loading dll_extra_paths" in caplog.records[0].message

    def test_reading_config_file_for_dll_extra_paths(self, monkeypatch):
        sys.platform = "win32"
        sys.version_info = (3, 8, 1)
        monkeypatch.setattr(
            os, "add_dll_directory", lambda *args, **kwargs: "", raising=False
        )
        config = ConfigParser()
        config["Paths"] = {}
        config["Paths"]["dll_extra_paths"] = r"C:\Program Files;C:\Program Files (x86)"
        with open(self.config_path, "w") as f:
            config.write(f)
        assert util.add_user_dll_extra_paths() == [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]

    def test_no_section_for_dll_extra_paths(self, monkeypatch, caplog):
        sys.platform = "win32"
        sys.version_info = (3, 8, 1)
        monkeypatch.setattr(
            os, "add_dll_directory", lambda *args, **kwargs: "", raising=False
        )
        config = ConfigParser()
        with open(self.config_path, "w") as f:
            config.write(f)
        with caplog.at_level(level=logging.DEBUG):
            assert util.add_user_dll_extra_paths() is None
        assert "NoOptionError or NoSectionError" in caplog.records[1].message

    def test_no_key_for_dll_extra_paths(self, monkeypatch, caplog):
        sys.platform = "win32"
        sys.version_info = (3, 8, 1)
        monkeypatch.setattr(
            os, "add_dll_directory", lambda *args, **kwargs: "", raising=False
        )
        config = ConfigParser()
        config["Paths"] = {}
        with open(self.config_path, "w") as f:
            config.write(f)
        with caplog.at_level(level=logging.DEBUG):
            assert util.add_user_dll_extra_paths() is None
        assert "NoOptionError or NoSectionError" in caplog.records[1].message

    def test_no_config_file_for_dll_extra_paths(self, monkeypatch, caplog):
        sys.platform = "win32"
        sys.version_info = (3, 8, 1)
        monkeypatch.setattr(
            os, "add_dll_directory", lambda *args, **kwargs: "", raising=False
        )
        with caplog.at_level(level=logging.DEBUG):
            assert util.add_user_dll_extra_paths() is None
        assert "No user defined" in caplog.records[0].message


class TestParser(BaseTestCase):
    def test_parse_binary(self):
        s = (
            b"#0@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xe2\x8b<@\xde\x8b<@\xde\x8b<@"
            b"\xde\x8b<@\xde\x8b<@\xe0\x8b<@\xe0\x8b<@\xdc\x8b<@\xde\x8b<@"
            b"\xe2\x8b<@\xe0\x8b<"
        )
        e = [
            0.01707566,
            0.01707566,
            0.01707566,
            0.01707566,
            0.01707375,
            0.01707375,
            0.01707375,
            0.01707375,
            0.01707470,
            0.01707470,
            0.01707280,
            0.01707375,
            0.01707566,
            0.01707470,
        ]

        # Test handling indefinite length block
        p = util.from_ieee_block(s, datatype="f", is_big_endian=False)
        for a, b in zip(p, e):
            assert a == pytest.approx(b)

        # Test handling definite length block
        p = util.from_ieee_block(b"#214" + s[2:], datatype="f", is_big_endian=False)
        for a, b in zip(p, e):
            assert a == pytest.approx(b)

        # Test handling zero length block
        p = util.from_ieee_block(b"#10" + s[2:], datatype="f", is_big_endian=False)
        assert not p

        p = util.from_hp_block(
            b"#A\x0e\x00" + s[2:],
            datatype="f",
            is_big_endian=False,
            container=partial(array.array, "f"),
        )
        for a, b in zip(p, e):
            assert a == pytest.approx(b)

    def test_integer_ascii_block(self):
        values = list(range(99))
        for fmt in "d":
            msg = "block=%s, fmt=%s"
            msg = msg % ("ascii", fmt)
            # Test handling the case of a trailing comma
            tb = lambda values: util.to_ascii_block(values, fmt, ",") + ","
            fb = lambda block, cont: util.from_ascii_block(block, fmt, ",", cont)
            self.round_trip_block_conversion(values, tb, fb, msg)

    def test_non_integer_ascii_block(self):
        values = [val + 0.5 for val in range(99)]
        values = list(range(99))
        for fmt in "fFeEgG":
            msg = "block=%s, fmt=%s"
            msg = msg % ("ascii", fmt)
            tb = lambda values: util.to_ascii_block(values, fmt, ",")
            fb = lambda block, cont: util.from_ascii_block(block, fmt, ",", cont)
            self.round_trip_block_conversion(values, tb, fb, msg)

    def test_invalid_string_converter(self):
        with pytest.raises(ValueError) as ex:
            util.to_ascii_block([1, 2], "m")
        assert "unsupported format character" in ex.exconly()
        with pytest.raises(ValueError) as ex:
            util.from_ascii_block("1,2,3", "m")
        assert "Invalid code for converter" in ex.exconly()

    def test_function_separator(self):
        values = list(range(99))
        fmt = "d"
        msg = "block=ascii, fmt=%s" % fmt
        tb = lambda values: util.to_ascii_block(values, fmt, ":".join)
        fb = lambda block, cont: util.from_ascii_block(
            block, fmt, lambda s: s.split(":"), cont
        )
        self.round_trip_block_conversion(values, tb, fb, msg)

    def test_function_converter(self):
        values = list(range(99))
        msg = "block=ascii"
        tb = lambda values: util.to_ascii_block(values, str, ":".join)
        fb = lambda block, cont: util.from_ascii_block(
            block, int, lambda s: s.split(":"), cont
        )
        self.round_trip_block_conversion(values, tb, fb, msg)

    def test_integer_binary_block(self):
        values = list(range(99))
        for block, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            for fmt in "bBhHiIfd":
                for endi in (True, False):
                    msg = "block=%s, fmt=%s, endianness=%s"
                    msg = msg % (block, fmt, endi)
                    tblock = lambda values: tb(values, fmt, endi)
                    fblock = lambda block, cont: fb(block, fmt, endi, cont)
                    self.round_trip_block_conversion(values, tblock, fblock, msg)

    def test_noninteger_binary_block(self):
        values = [val + 0.5 for val in range(99)]
        for block, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            for fmt in "fd":
                for endi in (True, False):
                    msg = "block=%s, fmt=%s, endianness=%s"
                    msg = msg % (block, fmt, endi)
                    tblock = lambda values: bytearray(tb(values, fmt, endi))
                    fblock = lambda block, cont: fb(block, fmt, endi, cont)
                    self.round_trip_block_conversion(values, tblock, fblock, msg)

    def test_bytes_binary_block(self):
        values = b"dbslbw cj saj \x00\x76"
        for block, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            for fmt in "sp":
                block = tb(values, datatype="s")
                print(block)
                rt = fb(block, datatype="s", container=bytes)
                assert values == rt

    def test_malformed_binary_block_header(self):
        values = list(range(10))
        for header, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            block = tb(values, "h", False)
            bad_block = block[1:]
            with pytest.raises(ValueError) as e:
                fb(bad_block, "h", False, list)

            assert "(#" in e.exconly()

    def test_weird_binary_block_header(self):
        values = list(range(100))
        for header, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            block = tb(values, "h", False)
            bad_block = block[1:]
            if header == "hp":
                index = bad_block.find(b"#")
                bad_block = bad_block[:index] + b"#A" + bad_block[index + 2 :]
            with pytest.warns(UserWarning):
                fb(bad_block, "h", False, list)

    def test_weird_binary_block_header_raise(self):
        values = list(range(100))
        for header, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            block = tb(values, "h", False)
            bad_block = block[1:]
            if header == "hp":
                index = bad_block.find(b"#")
                bad_block = bad_block[:index] + b"#A" + bad_block[index + 2 :]
            parse = (
                util.parse_ieee_block_header
                if header == "ieee"
                else partial(util.parse_hp_block_header, is_big_endian=False)
            )

            with pytest.raises(RuntimeError):
                parse(bad_block, raise_on_late_block=True)

            parse(bad_block, length_before_block=1000)

    def test_binary_block_shorter_than_advertized(self):
        values = list(range(99))
        for header, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            block = tb(values, "h", False)
            if header == "ieee":
                header_byte_number = int(block[1])
                block = (
                    block[:2]
                    + b"9" * header_byte_number
                    + block[2 + header_byte_number :]
                )
            else:
                block = block[:2] + b"\xff\xff\xff\xff" + block[2 + 4 :]
            with pytest.raises(ValueError) as e:
                fb(block, "h", False, list)

            assert "Binary data is incomplete" in e.exconly()

    def test_guessing_block_length(self):
        values = list(range(99))
        for header, tb, fb in zip(
            ("ieee", "hp"),
            (util.to_ieee_block, util.to_hp_block),
            (util.from_ieee_block, util.from_hp_block),
        ):
            block = tb(values, "h", False) + b"\n"
            if header == "ieee":
                header_length = int(block[1:2].decode())
                block = block[:2] + b"0" * header_length + block[2 + header_length :]
            else:
                block = block[:2] + b"\x00\x00\x00\x00" + block[2 + 4 :]
            assert not fb(block, "h", False, list)

    def test_handling_malformed_binary(self):
        containers = (list, tuple) + ((np.array, np.ndarray) if np else ())

        # Use this to generate malformed data which should in theory be
        # impossible
        class DumbBytes(bytes):
            def __len__(self):
                return 10

        for container in containers:
            with pytest.raises(ValueError) as e:
                util.from_binary_block(DumbBytes(b"\x00\x00\x00"), container=container)
            assert (
                "malformed" if container in (list, tuple) else "buffer" in e.exconly()
            )

    def round_trip_block_conversion(self, values, to_block, from_block, msg):
        """Test that block conversion round trip as expected."""
        containers = (list, tuple) + ((np.array,) if np else ())
        for cont in containers:
            conv = cont(values)
            msg += ", container=%s"
            msg = msg % cont.__name__
            try:
                block = to_block(conv)
                parsed = from_block(block, cont)
            except Exception as e:
                raise Exception(msg + "\n" + repr(e))

            if np and cont in (np.array,):
                np.testing.assert_array_equal(conv, parsed, msg)
            else:
                assert conv == parsed, msg


class TestSystemDetailsAnalysis(BaseTestCase):
    """Test getting the system details."""

    def setup_method(self):
        self._unicode_size = sys.maxunicode

    def teardown_method(self):
        sys.maxunicode = self._unicode_size

    def test_getting_system_details(self):
        sys.maxunicode = 65535
        path = os.path.join(os.path.dirname(__file__), "fake-extensions")
        sys.path.append(path)
        try:
            details = util.get_system_details(True)
        finally:
            sys.path.remove(path)
        assert details["backends"]
        assert details["unicode"] == "UCS2"

        sys.maxunicode = 1114111
        details = util.get_system_details(False)
        assert not details["backends"]
        assert details["unicode"] == "UCS4"

    def test_get_debug_info(self):
        details = util.system_details_to_str(util.get_system_details())
        assert util.get_debug_info(False) == details
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            util.get_debug_info()
        output = temp_stdout.getvalue()
        assert output.strip() == details.strip()

    def test_system_details_for_plugins(self):
        """Test reporting on plugins."""

        def dummy_list_backends():
            return ["test1", "test2", "test3", "test4"]

        def dummy_get_wrapper_class(backend):
            if backend == "test1":
                return IVIVisaLibrary

            elif backend == "test2":

                class BrokenBackend:
                    @classmethod
                    def get_debug_info(cls):
                        raise Exception()

                return BrokenBackend

            elif backend == "test4":

                class WeirdBackend:
                    @classmethod
                    def get_debug_info(cls):
                        return {"": {"": [object()]}}

                return WeirdBackend

            else:
                raise Exception()

        old_lb = highlevel.list_backends
        old_gwc = highlevel.get_wrapper_class
        highlevel.list_backends = dummy_list_backends
        highlevel.get_wrapper_class = dummy_get_wrapper_class

        try:
            details = util.get_system_details()
        finally:
            highlevel.list_backends = old_lb
            highlevel.get_wrapper_class = old_gwc

        assert "Could not instantiate" in details["backends"]["test3"][0]
        assert "Could not obtain" in details["backends"]["test2"][0]
        assert "Version" in details["backends"]["test1"]
        assert "" in details["backends"]["test4"]

        # Test converting the details to string
        util.system_details_to_str(details)


def generate_fakelibs(dirname):

    for name, blob in zip(
        [
            "fakelib_bad_magic.dll",
            "fakelib_good_32.dll",
            "fakelib_good_64_2.dll",
            "fakelib_good_64.dll",
            "fakelib_good_unknown.dll",
            "fakelib_not_pe.dll",
        ],
        [
            struct.pack("=6sH52sl", b"MAPE\x00\x00", 0x014C, 52 * b"\0", 2),
            struct.pack("=6sH52sl", b"MZPE\x00\x00", 0x014C, 52 * b"\0", 2),
            struct.pack("=6sH52sl", b"MZPE\x00\x00", 0x8664, 52 * b"\0", 2),
            struct.pack("=6sH52sl", b"MZPE\x00\x00", 0x0200, 52 * b"\0", 2),
            struct.pack("=6sH52sl", b"MZPE\x00\x00", 0xFFFF, 52 * b"\0", 2),
            struct.pack("=6sH52sl", b"MZDE\x00\x00", 0x014C, 52 * b"\0", 2),
        ],
    ):
        with open(os.path.join(dirname, name), "wb") as f:
            f.write(blob)
            print("Written %s" % name)


class TestLibraryAnalysis(BaseTestCase):
    """Test (through monkey patching) the analysis of binary libraries."""

    def test_get_shared_library_arch(self, tmpdir):
        """Test analysing a library on Windows."""
        dirname = str(tmpdir)
        generate_fakelibs(dirname)

        for f, a in zip(["_32", "_64", "_64_2"], ["I386", "IA64", "AMD64"]):
            arch = util.get_shared_library_arch(
                os.path.join(tmpdir, "fakelib_good%s.dll" % f)
            )
            assert arch == a

        arch = util.get_shared_library_arch(
            os.path.join(dirname, "fakelib_good_unknown.dll")
        )
        assert arch == "UNKNOWN"

        with pytest.raises(Exception) as e:
            util.get_shared_library_arch(os.path.join(dirname, "fakelib_bad_magic.dll"))
        assert "Not an executable" in e.exconly()

        with pytest.raises(Exception) as e:
            util.get_shared_library_arch(os.path.join(dirname, "fakelib_not_pe.dll"))
        assert "Not a PE executable" in e.exconly()

    def test_get_arch_windows(self, tmpdir):
        """Test identifying the computer architecture on windows."""
        dirname = str(tmpdir)
        generate_fakelibs(dirname)

        platform = sys.platform
        sys.platform = "win32"
        try:
            for f, a in zip(
                ["_32", "_64", "_64_2", "_unknown"], [(32,), (64,), (64,), ()]
            ):
                print(f, a)
                path = os.path.join(dirname, "fakelib_good%s.dll" % f)
                lib = util.LibraryPath(path)
                assert lib.arch == a
                if f != "_unknown":
                    assert lib.is_32bit if 32 in a else not lib.is_32bit
                    assert lib.is_64bit if 64 in a else not lib.is_64bit
                    assert lib.bitness == ", ".join(str(b) for b in a)
                else:
                    assert lib.is_32bit == "n/a"
                    assert lib.is_64bit == "n/a"
                    assert lib.bitness == "n/a"
        finally:
            sys.platform = platform

    @pytest.mark.skipif(sys.version_info < (3, 7), reason="Fails weirdly on Python 3.6")
    def test_get_arch_unix(self):
        """Test identifying the computer architecture on linux and Mac."""
        platform = sys.platform
        run = subprocess.run
        try:

            def alt_run(*args, **kwargs):
                if platform.startswith("win"):
                    kwargs["shell"] = True
                return run(["echo", args[0][1]], *args[1:], **kwargs)

            subprocess.run = alt_run

            for p, f, a in [
                ("linux2", "32-bit", (32,)),
                ("linux2", "32-bit & 64-bit", (32, 64)),
                ("linux3", "64-bit", (64,)),
                ("darwin", "(for architecture i386)", (32,)),
                ("darwin", "(for architecture x86_64)", (64,)),
            ]:
                sys.platform = p
                lib = util.LibraryPath(f)
                assert lib.arch == a
                assert lib.is_32bit if 32 in a else not lib.is_32bit
                assert lib.is_64bit if 64 in a else not lib.is_64bit
                assert lib.bitness == ", ".join(str(b) for b in a)

        finally:
            sys.platform = platform
            subprocess.run = run

    def test_get_arch_unix_unreported(self):
        """Test identifying the computer architecture on an unknown platform."""
        platform = sys.platform
        run = subprocess.run
        try:
            sys.platform = "darwin"
            lib = util.LibraryPath("")
            assert lib.arch == ()
            assert lib.is_32bit == "n/a"
            assert lib.is_64bit == "n/a"
            assert lib.bitness == "n/a"
        finally:
            sys.platform = platform
            subprocess.run = run

    def test_get_arch_unknown(self):
        """Test identifying the computer architecture on an unknown platform."""
        platform = sys.platform
        run = subprocess.run
        try:
            sys.platform = "test"
            lib = util.LibraryPath("")
            assert lib.arch == ()
            assert lib.is_32bit == "n/a"
            assert lib.is_64bit == "n/a"
            assert lib.bitness == "n/a"
        finally:
            sys.platform = platform
            subprocess.run = run
