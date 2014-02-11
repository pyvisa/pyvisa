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
    >>> my_instrument = rm.get_instrument('GPIB::14')
    >>> my_instrument.write("*IDN?")
    >>> print(my_instrument.read())

This example already shows the two main design goals of PyVISA: preferring
simplicity over generality, and doing it the object-oriented way.

Afer importing `visa`, we create a `ResourceManager` object. If called without
arguments, PyVISA will try to find the VISA shared for you. You can check, the
location of the shared library used simply by:

    >>> print(rm)
    <ResourceManager('/path/to/visa.so')>

.. note:: In some cases, PyVISA is not able to find the library for you
          resulting in an `OSError`. To fix it, find the library path
          yourself and pass it to the ResourceManager constructor.
          You can also specify it in a configuration file as discussed
          in :ref:`configuring`.


Once that you havea `ResourceManager`, you can access any instrument.
Every instrument is represented in the source by an object instance.
In this case, I have a GPIB instrument with instrument number 14, so I
create the instance (i.e. variable) called *my_instrument*
accordingly with `"GPIB::14"` is the instrument's *resource name*.
Notice that eventhough you have requeste an instrument, due to the
resource name, `get_instrument` has given you an instance of `GpibInstrument`
class (a subclass of the more generic instrument).

    >>> print(my_instrument)
    GpibInstrument('GPIB::14')

See section :ref:`sec:visa-resource-names` for a short explanation of that.
Then, I send the message `"\*IDN?"` to the device, which is the standard GPIB
message for "what are you?" or -- in some cases -- "what's on your
display at the moment?".


Listing connected instruments
-----------------------------

The resource manager object allows you to list available resources::

    >>> rm.list_resources()
    ['ASRL1', 'ASRL2']


or the most comprehensive `list_resources_info` which return a dict mapping
resource name to a namedtuple containing information such as the interface type
and the resource class.


Example for serial (RS232) device
---------------------------------

There is no only RS232 device in my lab is an old Oxford ITC4 temperature
controller, which is connected through COM2 with my computer.  The
following code prints its self-identification on the screen::
   
   itc4 = rm.get_instrument("COM2")
   itc4.write("V")
   print(itc4.read())

Instead of separate write and read operations, you can do both with
one `ask()` call. Thus, the above source code is equivalent to::

   from visa import *
   
   itc4 = instrument("COM2")
   print(itc4.ask("V"))

It couldn't be simpler.  See section :ref:`sec:serial-devices` for
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

   >>> keithley = rm.get_instrument("GPIB::12")
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
however, then we'd get

.. code-block:: none

   NDCV-000.0004E+0,NDCV-000.0005E+0,NDCV-000.0004E+0,NDCV-000.0007E+0,
   NDCV-000.0000E+0,NDCV-000.0007E+0,NDCV-000.0008E+0,NDCV-000.0004E+0,
   NDCV-000.0002E+0,NDCV-000.0005E+0

which we would have to convert to a Python list of numbers.
Fortunately, the `ask_for_values()` method does this work for us::

   >>> voltages = keithley.ask_for_values("trace:data?")
   >>> print("Average voltage: ", sum(voltages) / len(voltages))

Finally, we should reset the instrument's data buffer and SRQ status
register, so that it's ready for a new run.  Again, this is explained
in detail in the instrument's manual::

   >>> keithley.ask("status:measurement?")
   >>> keithley.write("trace:clear; feed:control next")

That's it.  18 lines of lucid code.  (Well, SCPI is awkward, but
that's another story.)


.. _sec:visa-resource-names:


VISA resource names
-------------------

If you use the function :func:`get_instrument`, you must tell this
function the *VISA resource name* of the instrument you want to
connect to.  Generally, it starts with the bus type, followed by a
double colon `"::"`, followed by the number within the bus.  For
example,

.. code-block:: none

   GPIB::10

denotes the GPIB instrument with the number 10.  If you have two GPIB
boards and the instrument is connected to board number 1, you must
write

.. code-block:: none

   GPIB1::10

As for the bus, things like `"GPIB"`, `"USB"`, `"ASRL"` (for
serial/parallel interface) are possible.  So for connecting to an
instrument at COM2, the resource name is

.. code-block:: none

   ASRL2

(Since only one instrument can be connected with one serial interface,
there is no double colon parameter.)  However, most VISA systems allow
aliases such as `"COM2"` or `"LPT1"`.  You may also add your own
aliases.

The resource name is case-insensitive.  It doesn't matter whether you
say `"ASRL2"` or `"asrl2"`.  For further information, I have to refer
you to a comprehensive VISA description like
`<http://www.ni.com/pdf/manuals/370423a.pdf>`_.

