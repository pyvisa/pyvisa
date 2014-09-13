.. _architecture:

Architecture
============

PyVISA implements convenient and Pythonic programming in three layers:

 1. Low-level: A wrapper around the shared visa library.

    The wrapper defines the argument types and response types of each function,
    as well as the conversions between Python objects and foreign types.

    You will normally not need to access these functions directly. If you do,
    it probably means that we need to improve layer 2.

    All level 1 functions are **static methods** of `VisaLibrary`.

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

    All level 2 functions are **bound methods** of `VisaLibrary`.

 3. High-level: An object-oriented layer for `ResourceManager` and `Resource`

    The `ResourceManager` implements methods to inspect connected resources. You also
    use this object to open other resources instantiating the appropriate `Resource`
    derived classes.

    `Resource` and the derived classes implement functions and attributes access
    to the underlying resources in a Pythonic way.

Most of the time you will only need to instantiate a `ResourceManager`. For a given resource,
you will use the `open_resource` method to obtain the appropriate object. If needed, you will
be able to access the `VisaLibrary` object directly using the `visalib` attribute.

The `VisaLibrary` does the low-level calls. In the default NI Backend, levels 1 and 2 are
implemented in the same package called `ctwrapper` (which stands for ctypes wrapper).
This package is included in PyVISA

But other backends can be used just by passing the name of the backend to `ResourceManager`
after the `@` symbol. See more information in :ref:`backends`.


Calling middle- and low-level functions
---------------------------------------

After you have instantiated the `ResourceManager`::

    >>> import visa
    >>> rm = visa.ResourceManager()

you can access corresponding the `VisaLibrary` instance under the `visalib` attribute.

You can recognize low an middle-level functions by their names. Low-level functions
carry the same name as in the shared library, and they are prefixed by `vi`.
Middle-level functions have a friendlier, more pythonic but still recognizable name.


Middle-level
~~~~~~~~~~~~

The `VisaLibrary` object exposes as bound methods the middle-level functions which are
one-to-one mapped from the foreing library.

Tipically, cameCase names where stripped from the leading `bi` and changed to underscore
separated lower case names. For example the VISA function `viMapAddress` appears
in the middle-level layer as `map_address`. The docs about these methods is
here :ref:`api`.


Low-level
~~~~~~~~~

You can also access the low-level functions as directly exposed as static methods,
for example::

    >>> rm.visalib.viMapAddress(<here goes the arguments>)

To call this functions you need to know the function declaration and how to
interface it to python. To help you out, the `VisaLibrary` object also contains
middle-level functions. Each middle-level function wraps one low-level function.
In this case::

    >>> rm.visalib.map_address(<here goes the arguments>)

The calling convention and types are handled by the wrapper.
