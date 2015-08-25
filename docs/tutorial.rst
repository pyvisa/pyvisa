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

After importing ``visa``, we create a ``ResourceManager`` object. If called without
arguments, PyVISA will use the default backend (NI) which tries to find the
VISA shared library for you. You can check, the location of the shared library
used simply by:

    >>> print(rm)
    <ResourceManager('/path/to/visa.so')>

.. note:: In some cases, PyVISA is not able to find the library for you
          resulting in an ``OSError``. To fix it, find the library path
          yourself and pass it to the ResourceManager constructor.
          You can also specify it in a configuration file as discussed
          in :ref:`configuring`.


Once that you have a ``ResourceManager``, you can list the available resources
using the ``list_resources`` method. The output is a tuple listing the
:ref:`resource_names`.

In this case, there is a GPIB instrument with instrument number 14, so you ask
the ``ResourceManager`` to open "'GPIB0::14::INSTR'" and assign the returned
object to the *my_instrument*.

Notice ``open_resource`` has given you an instance of ``GPIBInstrument`` class
(a subclass of the more generic ``Resource``).

    >>> print(my_instrument)
    <GPIBInstrument('GPIB::14')>

There many ``Resource`` subclasses representing the different types of resources, but
you do not have to worry as the ``ResourceManager`` will provide you with the appropiate
class. You can check the methods and attributes of each class in the :ref:`api_resources`

Then, you query the device with the following message: ``'\*IDN?'``.
Which is the standard GPIB message for "what are you?" or -- in some cases --
"what's on your display at the moment?". ``query`` is a short form for a ``write``
operation to send a message, followed by a ``read``.

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
one ``query()`` call. Thus, the above source code is equivalent to::

   print(itc4.query("V"))

It couldn't be simpler.


