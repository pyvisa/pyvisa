.. _intro-rvalues:

Reading and Writing values
==========================

.. include:: ../substitutions.sub

Some instruments allow to transfer to and from the computer larger datasets
with a single query. A typical example is an oscilloscope, which you can query
for the whole voltage trace. Or an arbitrary wave generator to which you
have to transfer the function you want to generate.

Basically, data like this can be transferred in two ways: in ASCII form (slow,
but human readable) and binary (fast, but more difficult to debug).

PyVISA Message Based Resources have different methods for this
called |read_ascii_values|, |query_ascii_values| and |read_binary_values|,
|query_binary_values|.


Reading ASCII values
--------------------

If your oscilloscope (open in the variable ``inst``) has been configured to
transfer data in **ASCII** when the ``CURV?`` command is issued, you can just
query the values like this::

    >>> values = inst.query_ascii_values('CURV?')

``values`` will be ``list`` containing the values from the device.

In many cases you do not want a ``list`` but rather a different container type
such as a ``numpy.array``. You can of course cast the data afterwards like
this::

    >>> values = np.array(inst.query_ascii_values('CURV?'))

but sometimes it is much more efficient to avoid the intermediate list, and in
this case you can just specify the container type in the query::

    >>> values = inst.query_ascii_values('CURV?', container=numpy.array)

In ``container``, you can have any callable/type that takes an iterable.

.. note::

    When using numpy.array or numpy.ndarray, PyVISA will use numpy routines to
    optimize the conversion by avoiding the use of an intermediate
    representation.

Some devices transfer data in ASCII but not as decimal numbers but rather hex
or oct. Or you might want to receive an array of strings. In that case you can
specify a ``converter``. For example, if you expect to receive integers as hex:

    >>> values = inst.query_ascii_values('CURV?', converter='x')

``converter`` can be one of the Python :ref:`string formatting codes <python:formatspec>`.
But you can also specify a callable that takes a single argument if needed.
The default converter is ``'f'``.

Finally, some devices might return the values separated in an uncommon way. For
example if the returned values are separated by a ``'$'`` you can do the
following call:

    >>> values = inst.query_ascii_values('CURV?', separator='$')

You can provide a function to takes a string and returns an iterable.
Default value for the separator is ``','`` (comma)

.. _sec:reading-binary-data:


Reading binary values
---------------------

If your oscilloscope (open in the variable ``inst``) has been configured to
transfer data in **BINARY** when the ``CURV?`` command is issued, you need to
know which type datatype (e.g. uint8, int8, single, double, etc) is being
used. PyVISA use the same naming convention as the
:ref:`struct module <python:format-characters>`.

You also need to know the *endianness*. PyVISA assumes little-endian as default.
If you have doubles `d` in big endian the call will be::

    >>> values = inst.query_binary_values('CURV?', datatype='d', is_big_endian=True)

You can also specify the output container type, just as it was shown before.

By default, PyVISA will assume that the data block is formatted according to
the IEEE convention. If your instrument uses HP data block you can pass
``header_fmt='hp'`` to ``read_binary_values``. If your instrument does not use
any header for the data simply ``header_fmt='empty'``.

By default PyVISA assumes, that the instrument will add the termination
character at the end of the data block and actually makes sure it reads it to
avoid issues. This behavior fits well a number of devices. However some devices
omit the termination character, in which cases the operation will timeout.
In this situation, first makes sure you can actually read from the instrument
by reading the answer using the ``read_raw`` function (you may need to call it
multiple time), and check that the advertized length of the block match what
you get from your instrument (plus the header). If it is so, then you can
safely pass ``expect_termination=False``, and PyVISA will not look for a
termination character at the end of the message.

An optional monitoring interface object, such as a tqdm progress bar, can be
passed to the read_binary_values() and query_binary_values() methods. This is useful
in applications where are large data records are downloaded from instruments such as
oscilloscopes.  Both methods will provide the monitoring object with an updated count
of the number of bytes read from the instrument. If monitoring object is a progress
bar, the progress bar must be initialized with the total number of bytes to be
downloaded from the instrument. The monitoring object must implement the update()
method. See the tqdm package documentation for more information.

A helper function (pyvisa.util.message_length) can be used to calculate the total
number of bytes in a data transfer, including the header and termination character.

An implementation of a progress bar might look like:

.. code:: python

    from pyvisa import resource_manager
    from pyvisa.util import message_length

    inst = resource_manager.open_resource(...)

    # calculate the total number of bytes to download
    total_bytes = message_length(num_points=1000, point_size=2, header_format="ieee")

    # create a download monitor and use it when downloading data
    with tqdm(desc="Downloading", unit="B", total=total_bytes) as progress_bar:
        inst.write("CURV?")
        data = inst.read_binary_values(monitoring_interface=progress_bar)

If you can read without any problem from your instrument, but cannot retrieve
the full message when using this method (VI_ERROR_CONN_LOST,
VI_ERROR_INV_SETUP, or Python simply crashes), try passing different values for
``chunk_size`` (the default is 20*1024). The underlying mechanism for this issue
is not clear but changing ``chunk_size`` has been used to work around it. Note
that using  larger chunk sizes for large transfer may result in a speed up of
the transfer.

In some cases, the instrument may use a protocol that does not indicate how
many bytes will be transferred. The Keithley 2000 for example always returns the
full buffer whose size is reported by the ``trace:points?`` command. Since a
binary block may contain the termination character, PyVISA needs to know how
many bytes to expect. For those case, you can pass the expected number of
points using the ``data_points`` keyword argument. The number of bytes will be
inferred from the datatype of the block.

Finally if you are reading a file for example and simply want to extract a bytes
object, you can use the ``"s"`` datatype and pass ``bytes`` as container.


Writing ASCII values
--------------------

To upload a function shape to arbitrary wave generator, the command might be
``WLISt:WAVeform:DATA <waveform name>,<function data>`` where
``<waveform name>`` tells the device under which name to store the data.

    >>> values = list(range(100))
    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values)

Again, you can specify the converter code.

    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values, converter='x')

``converter`` can be one of the Python :ref:`string formatting codes <python:formatspec>`.
But you can also specify a callable that takes a single argument if needed.
The default converter is ``'f'``.

The separator can also be specified just like in ``query_ascii_values``.

    >>> inst.write_ascii_values('WLISt:WAVeform:DATA somename,', values, converter='x', separator='$')

You can provide a function that takes a iterable and returns a string.
Default value for the separator is ``','`` (comma)


Writing binary values
---------------------

To upload a function shape to arbitrary wave generator, the command might be
``WLISt:WAVeform:DATA <waveform name>,<function data>`` where
``<waveform name>`` tells the device under which name to store the data.

    >>> values = list(range(100))
    >>> inst.write_binary_values('WLISt:WAVeform:DATA somename,', values)

Again you can specify the ``datatype`` and ``endianness``.

    >>> inst.write_binary_values('WLISt:WAVeform:DATA somename,', values, datatype='d', is_big_endian=False)

If your data are already in a ``bytes`` object you can use the ``"s"`` format.


When things are not what they should be
---------------------------------------

PyVISA provides an easy way to transfer data from and to the device. The
methods described above work fine for 99% of the cases but there is always a
particular device that do not follow any of the standard protocols and is so
different that it cannot be adapted with the arguments provided above.

In those cases, you need to get the data::

        >>> inst.write('CURV?')
        >>> data = inst.read_raw()

and then you need to implement the logic to parse it.

Alternatively if the `read_raw` call fails you can try to read just a few bytes
using::

        >>> inst.write('CURV?')
        >>> data = inst.read_bytes(1)

If this call fails it may mean that your instrument did not answer, either
because it needs more time or because your first instruction was not
understood.
