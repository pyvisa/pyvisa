.. _advanced:

Advanced
========


Calling middle- and low-level functions
----------------------------------------

Most of the time you will be accessing only the functions expose by the Resource.
But it is possible that you need a particular feature that has not been yet implemented
by PyVISA (by the way, let us know!)

For this, you can mix the high-level object-oriented approach described in this document
with middle- and low-level VISA function calls (See :ref:`architecture` for more
information). By doing so, you have full control of your devices:

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

.. warning:: Notice however that low-level functions might not be present in all wrapper
             implementations. For broader compatibility, do no use this layer unless really
             needed.


