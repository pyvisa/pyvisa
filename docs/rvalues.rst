.. _rvalues:

Writing and reading values
==========================

Some instruments allow to transfer to and from the computer larger datasets
with a single query. A typical example is an oscilloscope, which you can query
for the whole voltage trace. Or an arbitrary wave generator to which you
have to transfer the function you want to generate.

Basically, data like this can be transferred in two ways: in ASCII form (slow,
but human readable) and binary (fast, but more difficult to debug).

PyVISA Message Based Resources have two different methods for this called
`query_ascii_values` and `query_binary_values`. It also has the convenient
`query_values` which will use follow a previously established configuration.


Reading ASCII values
--------------------

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

Some devices transfer data in ASCII but not as decimal numbers but rather hex
or oct. Or you might want to receive an array of strings. In that case you can specify
a `converter`. For example, if you expect to receive integers as hex:

    >>> values = inst.query_ascii_values('CURV?', converter=lambda x: int(x, 16))

`converter` needs to be a callable that takes a single argument. The default converter
is `float`.

Finally, some devices might return the values separated in an uncommon way. You
can provide a function to takes a string and returns an iterable. You can also
provide a str, which will be interpreted as a separator value. For example if
the returned values are separated by a `'$'` you can do the following call:

    >>> values = inst.query_ascii_values('CURV?', separator='$')


.. _sec:reading-binary-data:


Reading binary values
---------------------

If your oscilloscope (open in the variable `inst`) has been configured to
transfer data in **BINARY** when the `CURV?` command is issued, you need to
know which type datatype (e.g. uint8, int8, single, double, etc) is being
used. PyVISA use the same naming convention as the :ref:`struct module <python:format-characters>`.

You also need to know the *endianness*. PyVISA assumes little-endian as default.
If you have doubles `d` in big endian the call will be::

    >>> values = inst.query_binary_values('CURV?', datatype='d', is_big_endian=True)

You can also specify the output container type, just as was shown before.

.. _sec:more-complex-example:

A more complex example
----------------------

The following example shows how to use SCPI commands with a Keithley
2000 multimeter in order to measure 10 voltages. After having read
them, the program calculates the average voltage and prints it on the
screen.

I'll explain the program step-by-step.  First, we have to initialise
the instrument::

   >>> keithley = rm.open_resource("GPIB::12")
   >>> keithley.write("*rst; status:preset; *cls")

Here, we create the instrument variable *keithley*, which is used for
all further operations on the instrument.  Immediately after it, we
send the initialisation and reset message to the instrument.

The next step is to write all the measurement parameters, in
particular the interval time (500ms) and the number of readings (10)
to the instrument.  I won't explain it in detail.  Have a look at an
SCPI and/or Keithley 2000 manual.

.. code-block:: python

   >>> interval_in_ms = 500
   >>> number_of_readings = 10
   >>> keithley.write("status:measurement:enable 512; *sre 1")
   >>> keithley.write("sample:count %d" % number_of_readings)
   >>> keithley.write("trigger:source bus")
   >>> keithley.write("trigger:delay %f" % (interval_in_ms / 1000.0))
   >>> keithley.write("trace:points %d" % number_of_readings)
   >>> keithley.write("trace:feed sense1; feed:control next")

Okay, now the instrument is prepared to do the measurement.  The next
three lines make the instrument waiting for a trigger pulse, trigger
it, and wait until it sends a "service request"::

   >>> keithley.write("initiate")
   >>> keithley.assert_trigger()
   >>> keithley.wait_for_srq()

With sending the service request, the instrument tells us that the
measurement has been finished and that the results are ready for
transmission.  We could read them with `keithley.query("trace:data?")`
however, then we'd get:

.. code-block:: none

   NDCV-000.0004E+0,NDCV-000.0005E+0,NDCV-000.0004E+0,NDCV-000.0007E+0,
   NDCV-000.0000E+0,NDCV-000.0007E+0,NDCV-000.0008E+0,NDCV-000.0004E+0,
   NDCV-000.0002E+0,NDCV-000.0005E+0

which we would have to convert to a Python list of numbers.
Fortunately, the `query_ascii_values()` method does this work for us::

   >>> voltages = keithley.query_ascii_values("trace:data?")
   >>> print("Average voltage: ", sum(voltages) / len(voltages))

Finally, we should reset the instrument's data buffer and SRQ status
register, so that it's ready for a new run.  Again, this is explained
in detail in the instrument's manual::

   >>> keithley.query("status:measurement?")
   >>> keithley.write("trace:clear; feed:control next")

That's it. 18 lines of lucid code.  (Well, SCPI is awkward, but
that's another story.)


Preconfiguring the transfer format
==================================

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

    >>> inst.values_format.use_binary('f', False, numpy.array)

After doing this, you can simply call::

    >>> inst.query_values('CURV?')

which will dispatch to the appropriate function and arguments.

If you want to default to ASCII transfer, hex, with `'$'` as separator:

    >>> inst.values_format.is_binary = False
    >>> inst.values_format.converter = lambda x: int(x, 16)
    >>> inst.values_format.separator = '$'
    >>> inst.values_format.container = numpy.array

or shorter:

    >>> inst.values_format.use_ascii(lambda x: int('x', 16), '$', numpy.array)



When things are not what they should be
=======================================

PyVISA provides an easy way to transfer data from and to the device. The methods
described above work fine for 99% of the cases but there is always a particular
device that do not follow any of th standard protocol and is so different that
cannot be adapted with the arguments provided above.

In those cases, you need to get the data::

        >>> inst.write('CURV?')
        >>> data = inst.read_raw()

and then you need to implement the logic to parse it. 


