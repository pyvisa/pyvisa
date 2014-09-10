.. _tutorial:

Tutorial
========

.. note:: If you have been using PyVISA before version 1.5, you might want to
          read :ref:`migrating`.


An example
----------

Let's go *in medias res* and have a look at a simple example::

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> rm.list_resources()
    ('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::14::INSTR')
    >>> my_instrument = rm.open_resource('GPIB0::14::INSTR')
    >>> print(my_instrument.query('*IDN?'))

This example already shows the two main design goals of PyVISA: preferring
simplicity over generality, and doing it the object-oriented way.

After importing `visa`, we create a `ResourceManager` object. If called without
arguments, PyVISA will use the default backend (NI) which tries to find the
VISA shared library for you. You can check, the location of the shared library
used simply by:

    >>> print(rm)
    <ResourceManager('/path/to/visa.so')>

.. note:: In some cases, PyVISA is not able to find the library for you
          resulting in an `OSError`. To fix it, find the library path
          yourself and pass it to the ResourceManager constructor.
          You can also specify it in a configuration file as discussed
          in :ref:`configuring`.


Once that you have a `ResourceManager`, you can list the available resources
using the `list_resources` method. The output is a tuple listing the
:ref:`sec:visa-resource-names`. See section :ref:`sec:visa-resource-names`
for a short explanation of that.

In this case, there is a GPIB instrument with instrument number 14, so you ask
the `ResourceManager` to open `"'GPIB0::14::INSTR'" and assign the returned
object to the *my_instrument*.

Notice `open_resource` has given you an instance of `GPIBInstrument` class
(a subclass of the more generic `Resource`).

    >>> print(my_instrument)
    <GPIBInstrument('GPIB::14')>

There many `Resource` subclasses representing the different types of resources, but
you do not have to worry as the `ResourceManager` will provide you with the appropiate
class. You can check the methods and attributes of each class in the :ref:`_api_resources`

Then, you query the device with the following message: `'\*IDN?'`.
Which is the standard GPIB message for "what are you?" or -- in some cases --
"what's on your display at the moment?". `query` is a short form for a `write`
operation to send a message, followed by a `read`.

So::

    >>> my_instrument.query("*IDN?")

is the same as::

    >>> my_instrument.write('*IDN?')
    >>> print(my_instrument.read())


Example for serial (RS232) device
---------------------------------

Consider an Oxford ITC4 temperature controller, which is connected
through COM2 with my computer.  The following code prints its
self-identification on the screen::
   
   itc4 = rm.open_resource("COM2")
   itc4.write("V")
   print(itc4.read())

Instead of separate write and read operations, you can do both with
one `query()` call. Thus, the above source code is equivalent to::

   print(itc4.query("V"))

It couldn't be simpler. See section :ref:`sec:serial-devices` for
further information about serial devices.


.. _sec:more-complex-example:

A more complex example
----------------------

The following example shows how to use SCPI commands with a Keithley
2000 multimeter in order to measure 10 voltages.  After having read
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
   >>> keithley.trigger()
   >>> keithley.wait_for_srq()

With sending the service request, the instrument tells us that the
measurement has been finished and that the results are ready for
transmission.  We could read them with `keithley.ask("trace:data?")`
however, then we'd get:

.. code-block:: none

   NDCV-000.0004E+0,NDCV-000.0005E+0,NDCV-000.0004E+0,NDCV-000.0007E+0,
   NDCV-000.0000E+0,NDCV-000.0007E+0,NDCV-000.0008E+0,NDCV-000.0004E+0,
   NDCV-000.0002E+0,NDCV-000.0005E+0

which we would have to convert to a Python list of numbers.
Fortunately, the `ask_for_values()` method does this work for us::

   >>> voltages = keithley.query_values("trace:data?")
   >>> print("Average voltage: ", sum(voltages) / len(voltages))

Finally, we should reset the instrument's data buffer and SRQ status
register, so that it's ready for a new run.  Again, this is explained
in detail in the instrument's manual::

   >>> keithley.ask("status:measurement?")
   >>> keithley.write("trace:clear; feed:control next")

That's it. 18 lines of lucid code.  (Well, SCPI is awkward, but
that's another story.)

