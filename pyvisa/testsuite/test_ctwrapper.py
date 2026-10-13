"""Test IVI buffer bookkeeping without loading a vendor VISA library."""

import gc
from types import SimpleNamespace
from weakref import ref

import pytest

from pyvisa import constants, highlevel
from pyvisa.ctwrapper import IVIVisaLibrary
from pyvisa.events import Event

from . import BaseTestCase


@pytest.fixture
def async_library():
    """Simulate viReadAsync while exercising the real Python wrapper."""
    library = object.__new__(IVIVisaLibrary)
    library._async_read_jobs = []
    next_job = 1

    def read_async(session, buffer, count, job_id):
        nonlocal next_job
        job_id._obj.value = next_job
        next_job += 1
        # Completion can occur before read_asynchronously returns.
        assert library.get_buffer_from_id(job_id._obj.value) is buffer
        buffer.value = b"abc"
        return constants.StatusCode.success

    library.lib = SimpleNamespace(viReadAsync=read_async)
    return library


class TestAsyncReadBuffers(BaseTestCase):
    def test_get_buffer_is_non_consuming(self, async_library):
        buffer, job_id, status = async_library.read_asynchronously(1, 8)
        assert status == constants.StatusCode.success
        assert async_library.get_buffer_from_id(job_id) is buffer
        assert async_library.get_buffer_from_id(job_id) is buffer
        assert len(async_library._async_read_jobs) == 1

    @pytest.mark.parametrize("index", [0, 1, 2])
    def test_pop_only_matching_job(self, async_library, index):
        reads = [async_library.read_asynchronously(1, 8) for _ in range(3)]
        buffer, job_id, _ = reads[index]
        remaining = [entry for i, entry in enumerate(reads) if i != index]

        assert async_library.get_buffer_from_id_and_pop(job_id) is buffer
        assert async_library.get_buffer_from_id(job_id) is None
        assert async_library.get_buffer_from_id_and_pop(job_id) is None
        assert len(async_library._async_read_jobs) == 2
        for (stored_id, stored_buffer), (expected_buffer, expected_id, _) in zip(
            async_library._async_read_jobs, remaining
        ):
            assert stored_id.value == expected_id
            assert stored_buffer is expected_buffer

    def test_pop_unknown_job_keeps_buffers(self, async_library):
        buffer, job_id, _ = async_library.read_asynchronously(1, 8)
        assert async_library.get_buffer_from_id_and_pop(job_id + 1) is None
        assert async_library.get_buffer_from_id(job_id) is buffer
        assert len(async_library._async_read_jobs) == 1

    def test_unreleased_buffer_is_retained(self, async_library):
        buffer, job_id, _ = async_library.read_asynchronously(1, 8)
        buffer_ref = ref(buffer)
        del buffer
        gc.collect()
        assert buffer_ref() is not None
        assert async_library.get_buffer_from_id(job_id) is buffer_ref()

    def test_pop_transfers_buffer_lifetime_to_caller(self, async_library):
        buffer, job_id, _ = async_library.read_asynchronously(1, 8)
        buffer_ref = ref(buffer)
        del buffer
        gc.collect()
        assert buffer_ref() is not None

        result = async_library.get_buffer_from_id_and_pop(job_id)
        assert result is buffer_ref()
        assert result.value == b"abc"
        gc.collect()
        assert buffer_ref() is result

        del result
        gc.collect()
        assert buffer_ref() is None

    def test_completed_reads_do_not_accumulate(self, async_library):
        buffers = []
        for _ in range(32):
            buffer, job_id, _ = async_library.read_asynchronously(1, 65536)
            buffers.append(ref(buffer))
            assert async_library.get_buffer_from_id_and_pop(job_id) is buffer
            assert not async_library._async_read_jobs
            del buffer

        gc.collect()
        assert all(buffer_ref() is None for buffer_ref in buffers)

    def test_completion_event_does_not_consume_buffer(self, async_library):
        buffer, job_id, _ = async_library.read_asynchronously(1, 8)

        def get_attribute(context, attribute):
            value = {
                constants.EventAttribute.job_id: job_id,
                constants.EventAttribute.return_count: 3,
            }[attribute]
            return value, constants.StatusCode.success

        async_library.get_attribute = get_attribute
        event = Event(async_library, constants.EventType.io_completion, 2)
        assert event.buffer is buffer
        assert event.data == b"abc"
        assert event.data == b"abc"
        assert len(async_library._async_read_jobs) == 1
        assert async_library.get_buffer_from_id_and_pop(event.job_id) is buffer
        assert event.buffer is None

    def test_job_id_can_be_reused_after_pop(self, async_library):
        buffer, job_id, _ = async_library.read_asynchronously(1, 8)
        assert async_library.get_buffer_from_id_and_pop(job_id) is buffer

        def reuse_job_id(session, new_buffer, count, result_id):
            result_id._obj.value = job_id
            assert async_library.get_buffer_from_id(job_id) is new_buffer
            new_buffer.value = b"new"
            return constants.StatusCode.success

        async_library.lib.viReadAsync = reuse_job_id
        new_buffer, new_id, _ = async_library.read_asynchronously(1, 8)
        assert new_id == job_id
        assert new_buffer is not buffer
        assert async_library.get_buffer_from_id_and_pop(new_id) is new_buffer
        assert new_buffer.value == b"new"
        assert not async_library._async_read_jobs

    def test_base_library_pop_is_unsupported(self):
        library = highlevel.VisaLibraryBase("test")
        with pytest.raises(NotImplementedError):
            library.get_buffer_from_id_and_pop(1)
