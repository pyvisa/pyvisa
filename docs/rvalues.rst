.. _rvalues:

Requesting values
=================

Some instruments allow to transfer to the computer larger datasets with a
single query. A typical example is an oscilloscope, which you can query for
the whole voltage trace.

Basically, data like this can be transferred in two ways: in ASCII form (slow,
but human readable) and binary (fast, but more difficult to debug). PyVISA
Message Based Resources have two different methods for this called
`query_ascii_values` and `query_binary_values`. It also has the convenient
`query_values` which will use follow a previously established configuration.


Reading ASCII data
------------------

If your oscilloscope (open in the variable `inst`) has been configured to
transfer data in **ASCII** when the `CURV?` command is issued, you can just
query the values like this::

    >>> values = inst.query_ascii_values('CURV?')

`values` will be `list` containing the values from the device.

In many cases you do not want a `list` but rather a different container type such
as a `numpy.array`. You can of course cast the data afterwards like this::

    >>> values = np.array(inst.query_ascii_values('CURV?'))

but sometimes it is much more efficient to avoid the intermediate list, and in this case
you can just specify the container type in the query::

    >>> values = inst.query_ascii_values('CURV?', container=numpy.array)

In `container` you can have any callable/type that takes an iterable.


.. _sec:reading-binary-data:


Reading binary data
-------------------

If your oscilloscope (open in the variable `inst`) has been configured to
transfer data in **BINARY** when the `CURV?` command is issued, you need to
know which type datatype (e.g. uint8, int8, single, double, etc) is being
used. PyVISA use the same naming convention as the :ref:`struct module <python:format-characters>`.

You also need to know the *endianness*. PyVISA assumes little-endian as default.
If you have doubles `d` in big endian the call will be::

    >>> values = inst.query_binary_values('CURV?', datatype='d', is_big_endian=True)

You can also specify the output container type, just as was shown before.


Preconfiguring the transfer format
----------------------------------

Most of the cases, each device will transfer data in the same format every time.
And making the call so detailed everytime can be annoying. For this purpose,
PyVISA provides a way to preconfigure the default. Each Message Based
Resources exposes an attribute named `values_format` which is an object with the following
properties: `is_binary`, `datatype`, `is_big_endian`, `container`. For example to set
e.g. little-endian floats and a numpy array::

    >>> inst.values_format.is_binary = True
    >>> inst.values_format.datatype = 'f'
    >>> inst.values_format.is_big_endian = False
    >>> inst.values_format.container = numpy.array

or shorter:

    >>> inst.values_format.define_binary('f', False, numpy.array)

After doing this, you can simply call::

    >>> inst.query_values('CURV?')

which will dispatch to the appropriate function and arguments.


