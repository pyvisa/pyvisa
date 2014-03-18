.. _migrating:

Migrating from PyVISA < 1.5
===========================

You don't need to change anything in your code if you only use the `instrument`
constructor; and attributes and methods of the resulting object.
For example, this code will run unchanged in modern versions of PyVISA::

    import visa
    keithley = visa.instrument("GPIB::12")
    print(keithley.ask("*IDN?"))

This covers almost every single program that I have seen on the internet.
However, if you use other parts of PyVISA or you are interested in the design
decisions behind the new version you might want to read on.

Some of these decisions were inspired by the `visalib` package as a part of Lantz_


Short summary
-------------

PyVISA 1.5 has full compatibility with previous versions of PyVISA (changing some
of the underlying implementation). But you are encouraged to do a few things
differently if you want to keep up with the latest developments:

**If you are doing:**

    >>> import visa
    >>> keithley = visa.instrument("GPIB::12")
    >>> print(keithley.ask("*IDN?"))

change it to:

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> keithley = rm.get_instrument("GPIB::12")
    >>> print(keithley.ask("*IDN?"))

**If you are doing:**

    >>> print(visa.get_instruments_list())

change it to:

    >>> print(rm.list_resources())

**If you are doing:**

    >>> import pyvisa.vpp43 as vpp43
    >>> vpp43.visa_library.load_library("/path/to/my/libvisa.so.7")

change it to:

    >>> import visa
    >>> lib = visa.VisaLibrary("/path/to/my/libvisa.so.7")


**If you are doing::**

    >>> vpp43.lock(session)

change it to::

    >>> lib.lock(session)


As you see, most of the code shown above is making a few things explict.
It adds 1 line of code (instantiating the VisaLibrary or ResourceManager object)
which is not a big deal but it makes things cleaner.

If you were using `printf`, `queryf`, `scanf`, `sprintf` or `sscanf` of `vpp43`,
rewrite as pure python code.


A more detailed description
---------------------------


Dropped support for string related functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The VISA library includes functions to search and manipulate strings such as `printf`,
`queryf`, `scanf`, `sprintf` and `sscanf`. This makes sense as visa involves a lot of
string handling operations. The original PyVISA implementation wrapped these functions.
But these operations are easily expressed in pure python and therefore were rarely used.

PyVISA 1.5 keeps these functions for backwards compatibility but it will be removed in 1.6.

We suggest that you replace such functions by a pure python version.


Isolated low-level wrapping module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, the low level implementation (`vpp43`) was
mixed with higher level constructs such as `VisaLibrary`, `VisaException` and error
messages. The VISA library was wrapped using ctypes.

In 1.5, we refactored it as `ctwrapper`, also a ctypes wrapper module but it only
depends on the constants definitions (`constants.py`). This allows us to test the
foreign function calls by isolating them from higher level abstractions. More importantly,
it also allows us to build new low level modules that can be used as drop in replacements
for `ctwrapper` in high level modules.

We have two modules planned:

- a Mock module that allows you to test a PyVISA program even if you do not have
  VISA installed.

- a CFFI based wrapper. CFFI is new python package that allows easier and more
  robust wrapping of foreign libraries. It might be part of Python in the future.

PyVISA 1.5 keeps `vpp43` in the legacy subpackage (reimplemented on top of `ctwrapper`)
to help with the migration but it will be removed in the future.

All functions that were present in `vpp43` are now present in `ctwrapper` but they
take an additional first parameter: the foreign library wrapper.

We suggest that you replace `vpp43` by using the new `VisaLibrary` object which provides
all foreign functions as bound methods (see below).


No singleton objects
~~~~~~~~~~~~~~~~~~~~

The original PyVISA implementation relied on a singleton, global objects for the
library wrapper (named `visa_library`, an instance of the old `pyvisa.vpp43.VisaLibrary`)
and the resource manager (named `resource_manager`, and instance of the old
`pyvisa.visa.ResourceManager`). These were instantiated on import and the user
could rebind to a different library using the `load_library` method. Calling this
method however did not affect `resource_manager` and might lead to an inconsistent
state.

In 1.5, there is a new `VisaLibrary` class and a new `ResourceManager` class (they are
both in `pyvisa.highlevel`). The new classes are not singletons, at least not in the
strict sense. Multiple instances of `VisaLibrary` and `ResourceManager` are possible,
but only if they refer to different foreign libraries. In code, this means:

    >>> lib1 = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> lib2 = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> lib3 = visa.VisaLibrary("/path/to/my/libvisa.so.8")
    >>> lib1 is lib2
    True
    >>> lib1 is lib3
    False

Most of the time, you will not need access to a `VisaLibrary` object but to a `ResourceManager`.
You can do:

    >>> lib = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> rm = lib.resource_manager

or equivalently:

    >>> rm = visa.ResourceManager("/path/to/my/libvisa.so.7")

.. note:: If the path for the library is not given, the path is obtained from
          the user settings file (if exists) or guessed from the OS.

You can still access the legacy classes and global objects::

    >>> from pyvisa.legacy import vpp43
    >>> from pyvisa.legacy import visa_library, resource_manager

In 1.5, `visa_library` and `resource_manager`, instances of the legacy classes,
will be instantiated on import.


VisaLibrary methods as way to call Visa functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the original PyVISA implementation, the `VisaLibrary` class was just having
a reference to the ctypes library and a few functions.

In 1.5, we introduced a new `VisaLibrary` class (`pyvisa.highlevel`) which has 
every single low level function defined in `ctwrapper` as bound methods. In code, 
this means that you can do::

    >>> import visa
    >>> lib = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> print(lib.read_stb(session))

It also has every single VISA foreign function in the underlying library as static
method. In code, this means that you can do::

    >>> lib = visa.VisaLibrary("/path/to/my/libvisa.so.7")
    >>> status = ctypes.c_ushort()
    >>> ret library.viReadSTB(session, ctypes.byref(status))
    >>> print(ret.value)


.. _Lantz: https://lantz.readthedocs.org/
