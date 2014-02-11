.. _advanced:

Advanced
========

You can mix the high-level object-oriented approach described in this document
with middle- and low-level VISA function calls (See :ref:`architecture` for more
information). By doing so, you have full control of your devices:

After you have instantiated the `ResourceManager`::

    >>> import visa
    >>> rm = visa.ResourceManager()

you can access corresponding the `VisaLibrary` instance under the `visalib`.
attribute. The `VisaLibrary` object contains low-level functions as directly
exposed by the foreign library, for example::

    >>> rm.visalib.viMapAddress(<here goes the arguments>)

To call this functions you need to know the function declaration and how to
interface it to python. To help you out, the `VisaLibrary` object also contains
middle-level functions. Each middle-level function wraps one low-level function.
In this case::

    >>> rm.visalib.map_address(<here goes the arguments>)

The calling convention and types are handled by the wrapper.

You can recognize low an middle-level functions by their names. Low-level functions
carry the same name as in the shared library, and they are prefixed by `vi`.
Middle-level functions have a friendlier, more pythonic but still recognizable name.
