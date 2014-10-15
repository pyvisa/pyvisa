.. _backends:


A frontend for multiple backends
================================

A small historical note might help to make this section clearer. So bear with
with me for a couple of lines. Originally PyVISA was a Python wrapper to the VISA
library. More specifically, it was :py:mod:`ctypes` wrapper around the NI-VISA.
This approach worked fine but made it difficult to develop other ways to communicate
with instruments in platforms where NI-VISA was not available. Users had to change
they programs to use other packages with different API.

Since 1.6, PyVISA is a frontend to VISA. It provides a nice, Pythonic API and can
connect to multiple backends. Each backend exposes a class derived from VisaLibraryBase
that implements the low-level communication. The ctypes wrapper around NI-VISA is the
default backend (called `ni`) and is bundled with PyVISA for simplicity.

You can specify the backend to use when you instantiate the resource manager using the
`@` symbol. Remembering that `ni` is the default, this::

    >>> import visa
    >>> rm = visa.ResourceManager()

is the same as this::

    >>> import visa
    >>> rm = visa.ResourceManager('@ni')

You can still provide the path to the library if needed::

    >>> import visa
    >>> rm = visa.ResourceManager('/path/to/lib@ni')

Under the hood, the `ResourceManager` looks for the requested backend and instantiate
the VISA library that it provides.

PyVISA locates backends by name. If you do:

    >>> import visa
    >>> rm = visa.ResourceManager('@somename')

PyVISA will try to import a package/module named `pyvisa-somename` which should be
installed in your system. This is a loosly coupled configuration free method.
PyVISA does not need to know about any backend out there until you actually
try to use it.

You can list the installed backends by running the following code in the command line:

    python -c "from pyvisa import highlevel; print(highlevel.list_backends())"

What does a minimum backend looks like? Quite simple::

    from pyvisa.highlevel import VisaLibraryBase

    class MyLibrary(VisaLibraryBase):
        pass

    WRAPPER_CLASS = MyLibrary

Additionally you can provide a staticmethod named get_debug_info that should return a
dictionary of debug information.
