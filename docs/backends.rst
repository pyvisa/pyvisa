.. _backends:


A frontend for multiple backends
================================

A small historical note might help to make this section clearer. So bear with
with me for a couple of lines. Originally PyVISA was a Python wrapper to the VISA
library. More specifically, it was :py:mod:`ctypes` wrapper around the NI-VISA.
This approach worked fine but made it difficult to develop other ways to communicate
with instruments in platforms where NI-VISA was not available. Users had to change
their programs to use other packages with different API.

Since 1.6, PyVISA is a frontend to VISA. It provides a nice, Pythonic API and can
connect to multiple backends. Each backend exposes a class derived from VisaLibraryBase
that implements the low-level communication. The ctypes wrapper around NI-VISA is the
default backend (called **ni**) and is bundled with PyVISA for simplicity.

You can specify the backend to use when you instantiate the resource manager using the
``@`` symbol. Remembering that **ni** is the default, this::

    >>> import visa
    >>> rm = visa.ResourceManager()

is the same as this::

    >>> import visa
    >>> rm = visa.ResourceManager('@ni')

You can still provide the path to the library if needed::

    >>> import visa
    >>> rm = visa.ResourceManager('/path/to/lib@ni')

Under the hood, the :class:`pyvisa.highlevel.ResourceManager` looks for the requested backend and instantiate
the VISA library that it provides.

PyVISA locates backends by name. If you do:

    >>> import visa
    >>> rm = visa.ResourceManager('@somename')

PyVISA will try to import a package/module named ``pyvisa-somename`` which should be
installed in your system. This is a loosly coupled configuration free method.
PyVISA does not need to know about any backend out there until you actually
try to use it.

You can list the installed backends by running the following code in the command line::

    python -m visa info


Developing a new Backend
------------------------

What does a minimum backend looks like? Quite simple::

    from pyvisa.highlevel import VisaLibraryBase

    class MyLibrary(VisaLibraryBase):
        pass

    WRAPPER_CLASS = MyLibrary

Additionally you can provide a staticmethod named get_debug_info` that should return a
dictionary of debug information which is printed when you call ``python -m visa info``

An important aspect of developing a backend is knowing which VisaLibraryBase method to
implement and what API to expose.

A **complete** implementation of a VISA Library requires a lot of functions (basically almost
all level 2 functions as described in :ref:`architecture` (there is also a complete list at the
bottom of this page). But a working implementation does not require all of them.

As a **very minimum** set you need:

    - **open_default_resource_manager**: returns a session to the Default Resource Manager resource.
    - **open**: Opens a session to the specified resource.
    - **close**: Closes the specified session, event, or find list.
    - **list_resources**: Returns a tuple of all connected devices matching query.

(you can get the signature below or here :ref:`api_visalibrarybase`)

But of course you cannot do anything interesting with just this. In general you will
also need:

    - **get_attribute**: Retrieves the state of an attribute.
    - **set_atribute**: Sets the state of an attribute.

If you need to start sending bytes to MessageBased instruments you will require:

    - **read**: Reads data from device or interface synchronously.
    - **write**: Writes data to device or interface synchronously.

For other usages or devices, you might need to implement other functions. Is really up to you
and your needs.

These functions should raise a :class:`pyvisa.errors.VisaIOError` or emit a :class:`pyvisa.errors.VisaIOWarning` if necessary.


Complete list of level 2 functions to implement::

    def read_memory(self, session, space, offset, width, extended=False):
    def write_memory(self, session, space, offset, data, width, extended=False):
    def move_in(self, session, space, offset, length, width, extended=False):
    def move_out(self, session, space, offset, length, data, width, extended=False):
    def peek(self, session, address, width):
    def poke(self, session, address, width, data):
    def assert_interrupt_signal(self, session, mode, status_id):
    def assert_trigger(self, session, protocol):
    def assert_utility_signal(self, session, line):
    def buffer_read(self, session, count):
    def buffer_write(self, session, data):
    def clear(self, session):
    def close(self, session):
    def disable_event(self, session, event_type, mechanism):
    def discard_events(self, session, event_type, mechanism):
    def enable_event(self, session, event_type, mechanism, context=None):
    def flush(self, session, mask):
    def get_attribute(self, session, attribute):
    def gpib_command(self, session, data):
    def gpib_control_atn(self, session, mode):
    def gpib_control_ren(self, session, mode):
    def gpib_pass_control(self, session, primary_address, secondary_address):
    def gpib_send_ifc(self, session):
    def in_8(self, session, space, offset, extended=False):
    def in_16(self, session, space, offset, extended=False):
    def in_32(self, session, space, offset, extended=False):
    def in_64(self, session, space, offset, extended=False):
    def install_handler(self, session, event_type, handler, user_handle):
    def list_resources(self, session, query='?*::INSTR'):
    def lock(self, session, lock_type, timeout, requested_key=None):
    def map_address(self, session, map_space, map_base, map_size,
    def map_trigger(self, session, trigger_source, trigger_destination, mode):
    def memory_allocation(self, session, size, extended=False):
    def memory_free(self, session, offset, extended=False):
    def move(self, session, source_space, source_offset, source_width, destination_space,
    def move_asynchronously(self, session, source_space, source_offset, source_width,
    def move_in_8(self, session, space, offset, length, extended=False):
    def move_in_16(self, session, space, offset, length, extended=False):
    def move_in_32(self, session, space, offset, length, extended=False):
    def move_in_64(self, session, space, offset, length, extended=False):
    def move_out_8(self, session, space, offset, length, data, extended=False):
    def move_out_16(self, session, space, offset, length, data, extended=False):
    def move_out_32(self, session, space, offset, length, data, extended=False):
    def move_out_64(self, session, space, offset, length, data, extended=False):
    def open(self, session, resource_name,
    def open_default_resource_manager(self):
    def out_8(self, session, space, offset, data, extended=False):
    def out_16(self, session, space, offset, data, extended=False):
    def out_32(self, session, space, offset, data, extended=False):
    def out_64(self, session, space, offset, data, extended=False):
    def parse_resource(self, session, resource_name):
    def parse_resource_extended(self, session, resource_name):
    def peek_8(self, session, address):
    def peek_16(self, session, address):
    def peek_32(self, session, address):
    def peek_64(self, session, address):
    def poke_8(self, session, address, data):
    def poke_16(self, session, address, data):
    def poke_32(self, session, address, data):
    def poke_64(self, session, address, data):
    def read(self, session, count):
    def read_asynchronously(self, session, count):
    def read_stb(self, session):
    def read_to_file(self, session, filename, count):
    def set_attribute(self, session, attribute, attribute_state):
    def set_buffer(self, session, mask, size):
    def status_description(self, session, status):
    def terminate(self, session, degree, job_id):
    def uninstall_handler(self, session, event_type, handler, user_handle=None):
    def unlock(self, session):
    def unmap_address(self, session):
    def unmap_trigger(self, session, trigger_source, trigger_destination):
    def usb_control_in(self, session, request_type_bitmap_field, request_id, request_value,
    def usb_control_out(self, session, request_type_bitmap_field, request_id, request_value,
    def vxi_command_query(self, session, mode, command):
    def wait_on_event(self, session, in_event_type, timeout):
    def write(self, session, data):
    def write_asynchronously(self, session, data):
    def write_from_file(self, session, filename, count):

