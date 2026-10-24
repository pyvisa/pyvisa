# -*- coding: utf-8 -*-
"""Test the message based resource helpers that do not need an instrument."""

import contextlib
import struct

import pytest

from pyvisa import constants
from pyvisa.resources.messagebased import MessageBasedResource


class FakeTermcharLibrary:
    """Serve a byte stream the way a backend does with the termchar enabled."""

    def __init__(self, data: bytes, termchar: bytes) -> None:
        self.data = data
        self.termchar = termchar

    def ignore_warning(self, session, *warnings_constants):
        return contextlib.nullcontext()

    def read(self, session, count):
        chunk = self.data[:count]
        status = constants.StatusCode.success_max_count_read
        index = chunk.find(self.termchar)
        if index >= 0:
            chunk = chunk[: index + 1]
            status = constants.StatusCode.success_termination_character_read
        elif len(chunk) < count:
            status = constants.StatusCode.success
        self.data = self.data[len(chunk) :]
        return chunk, status


@pytest.mark.parametrize(
    "values, datatype, is_big_endian",
    [
        # 2560 bytes: the big endian length starts with 0x0A
        (list(range(640)), "f", True),
        # 266 bytes: the little endian length starts with 0x0A
        (list(range(133)), "h", False),
    ],
)
def test_read_hp_block_whose_length_contains_the_termchar(
    values, datatype, is_big_endian
):
    endianess = ">" if is_big_endian else "<"
    data = struct.pack("%s%d%s" % (endianess, len(values), datatype), *values)
    header = b"#A" + struct.pack(endianess + "H", len(data))
    assert header[2:3] == b"\n"

    resource = MessageBasedResource.__new__(MessageBasedResource)
    resource.visalib = FakeTermcharLibrary(header + data + b"\n", b"\n")
    resource.session = 1
    resource._resource_name = "TEST"
    resource._read_termination = "\n"
    try:
        read = resource.read_binary_values(
            datatype=datatype, is_big_endian=is_big_endian, header_fmt="hp"
        )
    finally:
        resource.session = None

    assert read == values
    assert resource.visalib.data == b""
