.. _architecture:

Architecture
============

PyVISA implements convenient and Pythonic programming in three layers:

 1. Low-level: A wrapper around the shared visa library.

    The wrapper defines the argument types and response types of each function,
    as well as the conversions between Python objects and foreign types.

    You will normally not need to access these functions directly. If you do,
    it probably means that we need to improve layer 2.

    All level 1 functions are **static methods** of :class:`pyvisa.highlevel.VisaLibrary`.

    .. warning:: Notice however that low-level functions might not be present in all backends.
                 For broader compatibility, do no use this layer. All the functionality should
                 is available via the next layer.


 2. Middle-level: A wrapping Python function for each function of the shared visa library.

    These functions call the low-level functions, adding some code to deal with
    type conversions for functions that return values by reference.
    These functions also have comprehensive and Python friendly documentation.

    You only need to access this layer if you want to control certain specific
    aspects of the VISA library which are not implemented by the corresponding
    resource class.

    All level 2 functions are **bound methods** of :class:`pyvisa.highlevel.VisaLibrary`.

 3. High-level: An object-oriented layer for :class:`pyvisa.highlevel.ResourceManager` and :class:`pyvisa.resources.Resource`

    The ``ResourceManager`` implements methods to inspect connected resources. You also
    use this object to open other resources instantiating the appropriate ``Resource``
    derived classes.

    ``Resource`` and the derived classes implement functions and attributes access
    to the underlying resources in a Pythonic way.

Most of the time you will only need to instantiate a ``ResourceManager``. For a given resource,
you will use the :meth:`pyvisa.highlevel.ResourceManager.open_resource` method to obtain the appropriate object. If needed, you will
be able to access the ``VisaLibrary`` object directly using the :attr:`pyvisa.highlevel.ResourceManager.visalib` attribute.

The ``VisaLibrary`` does the low-level calls. In the default NI Backend, levels 1 and 2 are
implemented in the same package called :mod:`pyvisa.ctwrapper` (which stands for ctypes wrapper).
This package is included in PyVISA.

Other backends can be used just by passing the name of the backend to ``ResourceManager``
after the `@` symbol. See more information in :ref:`backends`.


Calling middle- and low-level functions
---------------------------------------

After you have instantiated the ``ResourceManager``::

    >>> import visa
    >>> rm = visa.ResourceManager()

you can access the corresponding ``VisaLibrary`` instance under the ``visalib`` attribute.

As an example, consider the VISA function ``viMapAddress``. It appears in the low-level
layer as the static method ``viMapAddress`` of ``visalib`` attributed and also appears
in the middle-level layer as ``map_address``.

You can recognize low and middle-level functions by their names. Low-level functions
carry the same name as in the shared library, and they are prefixed by **vi**.
Middle-level functions have a friendlier, more pythonic but still recognizable name.
Typically, camelCase names where stripped from the leading **vi** and changed to underscore
separated lower case names. The docs about these methods is located here :ref:`api`.


Low-level
~~~~~~~~~

You can access the low-level functions directly exposed as static methods,
for example::

    >>> rm.visalib.viMapAddress(<here goes the arguments>)

To call this functions you need to know the function declaration and how to
interface it to python. To help you out, the ``VisaLibrary`` object also contains
middle-level functions.

It is very likely that you will need to access the VISA constants using these methods.
You can find the information about these constants here :ref:`api_constants`


Middle-level
~~~~~~~~~~~~

The ``VisaLibrary`` object exposes the middle-level functions which are
one-to-one mapped from the foreign library as bound methods.

Each middle-level function wraps one low-level function.
In this case::

    >>> rm.visalib.map_address(<here goes the arguments>)

The calling convention and types are handled by the wrapper.

