.. _rvalues:

Reading and Writing values
==========================

Some instruments allow to transfer to and from the computer larger datasets
with a single query. A typical example is an oscilloscope, which you can query
for the whole voltage trace. Or an arbitrary wave generator to which you
have to transfer the function you want to generate.

Basically, data like this can be transferred in two ways: in ASCII form (slow,
but human readable) and binary (fast, but more difficult to debug).

PyVISA Message Based Resources have two different methods for this
called :meth:`pyvisa.resources.MessageBasedResource.query_ascii_values`
and :meth:`pyvisa.resources.MessageBasedResource.query_binary_values`.
It also has the convenient :meth:`pyvisa.resources.MessageBasedResource.query_values`
which will use follow a previously established configuration.


Reading ASCII values
--------------------

If your oscilloscope (open in the variable ``inst``) has been configured to
transfer data in **ASCII** when the ``CURV?`` command is issued, you can just
query the values like this::

    >>> values = inst.query_ascii_values('CURV?')

``values`` will be ``list`` containing the values from the device.

In many cases you do not want a ``list`` but rather a different container type such
as a ``numpy.array``. You can of course cast the data afterwards like this::

    >>> values = np.array(inst.query_ascii_values('CURV?'))

but sometimes it is much more efficient to avoid the intermediate list, and in this case
you can just specify the container type in the query::

    >>> values = inst.query_ascii_values('CURV?', container=numpy.array)

In ``container`` you can have any callable/type that takes an iterable.

Some devices transfer data in ASCII but not as decimal numbers but rather hex
or oct. Or you might want to receive an array of strings. In that case you can specify
a ``converter``. For example, if you expect to receive integers as hex:

    >>> values = inst.query_ascii_values('CURV?', converter='x')

``converter`` can be one of the Python :ref:`string formatting codes <python:formatspec>`.
But you can also specify a callable that takes a single argument if needed.
The default converter is ``'f'``.

Finally, some devices might return the values separated in an uncommon way. For example
if the returned values are separated by a ``'$'`` you can do the following call:

    >>> values = inst.query_ascii_values('CURV?', separator='$')

You can provide a function to takes a string and returns an iterable.
Default value for the separator is ``','`` (comma)

.. _sec:reading-binary-data:


Reading binary values
---------------------

If your oscilloscope (open in the variable ``inst``) has been configured to
transfer data in **BINARY** when the ``CURV?`` command is issued, you need to
know which type datatype (e.g. uint8, int8, single, double, etc) is being
used. PyVISA use the same naming convention as the :ref:`struct module <python:format-characters>`.

You also need to know the *endianness*. PyVISA assumes little-endian as default.
If you have doubles `d` in big endian the call will be::

    >>> values = inst.query_binary_values('CURV?', datatype='d', is_big_endian=True)

You can also specify the output container type, just as it was shown before.


Writing ASCII values
--------------------

To upload a function shape to arbitrary wave generator, the command might be
``WLISt:WAVeform:DATA <waveform name>,<function data>`` where ``<waveform name>``
tells the device under which name to store the data.

    >>> values = list(range(100))
    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values)

Again, you can specify the converter code.

    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values, converter='x')

``converter`` can be one of the Python :ref:`string formatting codes <python:formatspec>`.
But you can also specify a callable that takes a single argument if needed.
The default converter is ``'f'``.

The separator can also be specified just like in ``query_ascii_values``.

    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values, converter='x', separator='$')

You can provide a function to takes a iterable and returns an string.
Default value for the separator is ``','`` (comma)


Writing binary values
---------------------

To upload a function shape to arbitrary wave generator, the command might be
``WLISt:WAVeform:DATA <waveform name>,<function data>`` where ``<waveform name>``
tells the device under which name to store the data.

    >>> values = list(range(100))
    >>> inst.write_binary_values('WLISt:WAVeform:DATA somename,', values)

Again you can specify the ``datatype`` and ``endianness``.

    >>> inst.write_binary_values('WLISt:WAVeform:DATA somename,', values, datatype='d', is_big_endian=False)



Preconfiguring the transfer format
----------------------------------

Most of the cases, each device will transfer data in the same format every time.
And making the call so detailed everytime can be annoying. For this purpose,
PyVISA provides a way to preconfigure the default. Each Message Based
Resources exposes an attribute named ``values_format`` which is an object with the following
properties: ``is_binary``, ``datatype``, ``is_big_endian``, ``container``. For example to set
e.g. little-endian doubles and a numpy array::

    >>> inst.values_format.is_binary = True
    >>> inst.values_format.datatype = 'd'
    >>> inst.values_format.is_big_endian = False
    >>> inst.values_format.container = numpy.array

or shorter:

    >>> inst.values_format.use_binary('d', False, numpy.array)

After doing this, you can simply call::

    >>> inst.query_values('CURV?')

which will dispatch to the appropriate function and arguments.

If you want to default to ASCII transfer, preconfiguring is a little bit more
cumbersome as you need to specify the converters for both ways.

For example with hex, with ``'$'`` as separator:

    >>> inst.values_format.is_binary = False
    >>> inst.values_format.converter = 'x'
    >>> inst.values_format.separator = '$'
    >>> inst.values_format.container = numpy.array

or shorter:

    >>> inst.values_format.use_ascii('x', '$', numpy.array)


This works for both query and write operations.


When things are not what they should be
---------------------------------------

PyVISA provides an easy way to transfer data from and to the device. The methods
described above work fine for 99% of the cases but there is always a particular
device that do not follow any of the standard protocols and is so different that
cannot be adapted with the arguments provided above.

In those cases, you need to get the data::

        >>> inst.write('CURV?')
        >>> data = inst.read_raw()

and then you need to implement the logic to parse it.


