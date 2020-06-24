# -*- coding: utf-8 -*-
"""Generate binary files acting as false library files.

"""
import os
import struct

dirname = os.path.dirname(__file__)


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
