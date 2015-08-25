.. _migrating:

Migrating from PyVISA < 1.5
===========================

.. note:: if you want PyVISA 1.4 compatibility use PyVISA 1.5 that provides
          Python 3 support, better visa library detection heuristics,
          Windows, Linux and OS X support, and no singleton object.
          PyVISA 1.6+ introduces a few compatibility breaks.


Some of these decisions were inspired by the ``visalib`` package as a part of Lantz_


Short summary
-------------

PyVISA 1.5 has full compatibility with previous versions of PyVISA using the
legacy module (changing some of the underlying implementation). But you are
encouraged to do a few things differently if you want to keep up with the
latest developments and be compatible with PyVISA > 1.5.

Indeed PyVISA 1.6 breaks compatibility to bring across a few good things.

**If you are doing:**

    >>> import visa
    >>> keithley = visa.instrument("GPIB::12")
    >>> print(keithley.ask("*IDN?"))

change it to:

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> keithley = rm.open_resource("GPIB::12")
    >>> print(keithley.query("*IDN?"))

**If you are doing:**

    >>> print(visa.get_instruments_list())

change it to:

    >>> print(rm.list_resources())

**If you are doing:**

    >>> import pyvisa.vpp43 as vpp43
    >>> vpp43.visa_library.load_library("/path/to/my/libvisa.so.7")

change it to:

    >>> import visa
    >>> rm = visa.ResourceManager("/path/to/my/libvisa.so.7")
    >>> lib = rm.visalib


**If you are doing::**

    >>> vpp43.lock(session)

change it to::

    >>> lib.lock(session)

or better:

    >>> resource.lock()


**If you are doing::**

    >>> inst.term_chars = '\r'

change it to::

    >>> inst.read_termination = '\r'
    >>> inst.write_termination = '\r'

**If you are doing::**

    >>> print(lib.status)

change it to::

    >>> print(lib.last_status)

or even better, do it per resource::

    >>> print(rm.last_status) # for the resource manager
    >>> print(inst.last_status) # for a specific instrument

**If you are doing::**

    >>> inst.timeout = 1  # Seconds

change it to::

    >>> inst.timeout = 1000  # Milliseconds


As you see, most of the code shown above is making a few things explict.
It adds 1 line of code (instantiating the ResourceManager object)
which is not a big deal but it makes things cleaner.

If you were using ``printf``, ``queryf``, ``scanf``, ``sprintf`` or ``sscanf`` of ``vpp43``,
rewrite as pure Python code (see below).

If you were using ``Instrument.delay``, change your code or use ``Instrument.query_delay``
(see below).


A few alias has been created to ease the transition:

 - ask -> query
 - ask_delay -> query_delay
 - get_instrument -> open_resource


A more detailed description
---------------------------


Dropped support for string related functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The VISA library includes functions to search and manipulate strings such as ``printf``,
``queryf``, ``scanf``, ``sprintf`` and ``sscanf``. This makes sense as VISA involves a lot of
string handling operations. The original PyVISA implementation wrapped these functions.
But these operations are easily expressed in pure python and therefore were rarely used.

PyVISA 1.5 keeps these functions for backwards compatibility but they are removed in 1.6.

We suggest that you replace such functions by a pure Python version.


Isolated low-level wrapping module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, the low level implementation (``vpp43``) was
mixed with higher level constructs. The VISA library was wrapped using ctypes.

In 1.5, we refactored it as ``ctwrapper``. This allows us to test the
foreign function calls by isolating them from higher level abstractions.
More importantly, it also allows us to build new low level modules that
can be used as drop in replacements for ``ctwrapper`` in high level modules.

In 1.6, we made the ``ResourceManager`` the object exposed to the user. The type of the
``VisaLibrary`` can selected depending of the ``library_path`` and obtained from a plugin
package.

We have two of such packages planned:

- a Mock module that allows you to test a PyVISA program even if you do not have
  VISA installed.

- a CFFI based wrapper. CFFI is new python package that allows easier and more
  robust wrapping of foreign libraries. It might be part of Python in the future.

PyVISA 1.5 keeps ``vpp43`` in the legacy subpackage (reimplemented on top of ``ctwrapper``)
to help with the migration. This module is gone in 1.6.

All functions that were present in ``vpp43`` are now present in ``ctwrapper`` but they
take an additional first parameter: the foreign library wrapper.

We suggest that you replace ``vpp43`` by accessing the ``VisaLibrary`` object under the attribute
visalib of the resource manager which provides all foreign functions as bound methods (see below).


No singleton objects
~~~~~~~~~~~~~~~~~~~~

The original PyVISA implementation relied on a singleton, global objects for the
library wrapper (named ``visa_library``, an instance of the old ``pyvisa.vpp43.VisaLibrary``)
and the resource manager (named ``resource_manager``, and instance of the old
``pyvisa.visa.ResourceManager``). These were instantiated on import and the user
could rebind to a different library using the ``load_library`` method. Calling this
method however did not affect ``resource_manager`` and might lead to an inconsistent
state.

There were additionally a few global structures such a ``status`` which stored the last
status returned by the library and the warning context to prevent unwanted warnings.

In 1.5, there is a new ``VisaLibrary`` class and a new ``ResourceManager`` class (they are
both in ``pyvisa.highlevel``). The new classes are not singletons, at least not in the
strict sense. Multiple instances of ``VisaLibrary`` and ``ResourceManager`` are possible,
but only if they refer to different foreign libraries. In code, this means:

    >>> lib1 = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> lib2 = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> lib3 = visa.VisaLibrary("/path/to/my/libvisa.so.8")
    >>> lib1 is lib2
    True
    >>> lib1 is lib3
    False

Most of the time, you will not need access to a ``VisaLibrary`` object but to a ``ResourceManager``.
You can do:

    >>> lib = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> rm = lib.resource_manager

or equivalently:

    >>> rm = visa.ResourceManager("/path/to/my/libvisa.so.7")

.. note:: If the path for the library is not given, the path is obtained from
          the user settings file (if exists) or guessed from the OS.

In 1.6, the state returned by the library is stored per resource. Additionally,
warnings can be silenced by resource as well. You can access with the ``last_status``
property.

All together, these changes makes PyVISA thread safe.


VisaLibrary methods as way to call Visa functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, the ``VisaLibrary`` class was just having
a reference to the ctypes library and a few functions.

In 1.5, we introduced a new ``VisaLibrary`` class (``pyvisa.highlevel``) which has
every single low level function defined in ``ctwrapper`` as bound methods. In code,
this means that you can do::

    >>> import visa
    >>> rm = visa.ResourceManager("/path/to/my/libvisa.so.7")
    >>> lib = rm.visalib
    >>> print(lib.read_stb(session))

(But it is very likely that you do not have to do it as the resource should have the
function you need)

It also has every single VISA foreign function in the underlying library as static
method. In code, this means that you can do::

    >>> status = ctypes.c_ushort()
    >>> ret lib.viReadSTB(session, ctypes.byref(status))
    >>> print(ret.value)


Ask vs. query
~~~~~~~~~~~~~

Historically, the method ``ask`` has been used in PyVISA to do a ``write`` followed
by a ``read``. But in many other programs this operation is called ``query``. Thereby
we have decided to switch the name, keeping an alias to help with the transition.

However, ``ask_for_values`` has not been aliased to ``query_values`` because the API
is different. ``ask_for_values`` still uses the old formatting API which is limited
and broken. We suggest that you migrate everything to ``query_values``


Seconds to milliseconds
~~~~~~~~~~~~~~~~~~~~~~~

The timeout is now in milliseconds (not in seconds as it was before). The reason
behind this change is to make it coherent with all other VISA implementations out
there. The C-API, LabVIEW, .NET: all use milliseconds. Using the same units not
only makes it easy to migrate to PyVISA but also allows to profit from all other
VISA docs out there without extra cognitive effort.


Removal of Instrument.delay and added Instrument.query_delay
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, ``Instrument`` takes a ``delay``
argument that adds a pause after each write operation (This also can
be changed using the ``delay`` attribute).

In PyVISA 1.6, ``delay`` is removed. Delays after write operations must
be added to the application code. Instead, a new attribute and argument
``query_delay`` is available. This allows you to pause between ``write` and ``read``
operations inside ``query``. Additionally, ``query`` takes an optional argument
called ``query`` allowing you to change it for each method call.


Deprecated term_chars and automatic removal of CR + LF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, ``Instrument`` takes a ``term_chars``
argument to change at the read and write termination characters. If this
argument is ``None``, ``CR + LF`` is appended to each outgoing message and
not expected for incoming messages (although removed if present).

In PyVISA 1.6, ``term_chars`` is replaced by ``read_termination` and
``write_termination``. In this way, you can set independently the termination
for each operation. Automatic removal of ``CR + LF`` is also gone in 1.6.




.. _Lantz: https://lantz.readthedocs.org/
