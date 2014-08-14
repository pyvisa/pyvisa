.. _advanced:

Advanced
========


Requesting values
-----------------


.. _sec:reading-binary-data:

Reading binary data
-------------------

Some instruments allow for sending the measured data in binary form.  This has
the advantage that the data transfer is much smaller and takes less time.
PyVISA currently supports three forms of transfers:

ascii
   This is the default mode.  It assumes a normal string with comma-  or
   whitespace-separated values.

single
   The values are expected as a binary sequence of IEEE floating  point values with
   single precision (i.e. four bytes each).
   All  flavours of binary data streams defined in IEEE488.2 are supported,  i.e.
   those beginning with *<header>#<digit>*,
   where *<header>* is optional, and  *<digit>* may also be
   "0".

double
   The same as **single**, but with values of double precision  (eight bytes each).

You can set the form of transfer with the property `values_format`, either
with the generation of the object,

.. code-block:: python

   my_instrument = instrument("GPIB::12", values_format = single)

or later by setting the property directly::

   my_instrument.values_format = single

Setting this option affects the methods `read_values()` and
`ask_for_values()`.  In particular, you must assure separately that the
device actually sends in this format.    In some cases it may be necessary to
set the *byte order*, also known as  *endianness*.  PyVISA assumes little-endian
as default.  Some instruments  call this "swapped" byte order.  However, there
is also big-endian byte  order.  In this case you have to append `|
big_endian` to your values  format::

   my_instrument = instrument("GPIB::12", values_format = single | big_endian)


.. _sec:binary-example:


Example
~~~~~~~

In order to demonstrate how easy reading binary data can be, remember our
example from section :ref:`sec:more-complex-example`.  You just have to append
the lines

.. code-block:: python

   keithley.write("format:data sreal")
   keithley.values_format = single

to the initialisation commands, and all measurement data will be transmitted as
binary.  You will only notice the increased speed, as PyVISA converts it into
the same list of values as before.




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


