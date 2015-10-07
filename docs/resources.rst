.. _resources:

Resources
=========

A resource represents an instrument, e.g. a measurement device. There are
multiple classes derived from resources representing the different available
types of resources (eg. GPIB, Serial). Each contains the particular set of
attributes an methods that are available by the underlying device.

You do not create this objects directly but they are returned by the
:meth:`pyvisa.highlevel.ResourceManager.open_resource` method of a :class:`pyvisa.highlevel.ResourceManager`. In general terms, there
are two main groups derived from :class:`pyvisa.resources.Resource`, :class:`pyvisa.resources.RegisterBasedResource` and :class:`pyvisa.resources.MessageBasedResource`.

.. note:: The resource Python class to use is selected automatically from the
          resource name. However, you can force a Resource Python class:

          >>> from pyvisa.resources import MessageBasedResource
          >>> inst = rm.open('ASRL1::INSTR', resource_pyclass=MessageBasedResource)


The following sections explore the most common attributes of ``Resource`` and
``MessageBased`` (Serial, GPIB, etc) which are the ones you will encounte more
often. For more information, refer to the :ref:`api`.


Attributes Resource
-------------------

session
~~~~~~~

Each communication channel to an instrument has a session handle which is unique.
You can get this value::

    >>> my_device.session
    10442240

If the resource is closed, an exception will be raised:

    >>> inst.close()
    >>> inst.session
    Traceback (most recent call last):
    ...
    pyvisa.errors.InvalidSession: Invalid session handle. The resource might be closed.


timeout
~~~~~~~

Very most VISA I/O operations may be performed with a timeout. If a timeout is
set, every operation that takes longer than the timeout is aborted and an
exception is raised.  Timeouts are given per instrument in **milliseconds**.

For all PyVISA objects, a timeout is set with

.. code-block:: python

   my_device.timeout = 25000

Here, ``my_device`` may be a device, an interface or whatever, and its timeout is
set to 25 seconds. To set an **infinite** timeout, set it to ``None`` or ``float('+inf')`` or:

.. code-block:: python

   del my_device.timeout

To set it to **immediate**, set it to `0` or a negative value. (Actually, any value
smaller than 1 is considered immediate)

Now every operation of the resource takes as long as it takes, even
indefinitely if necessary.


Attributes of MessageBase resources
-----------------------------------

.. _sec:chunk-length:

Chunk length
~~~~~~~~~~~~

If you read data from a device, you must store it somewhere.  Unfortunately,
PyVISA must make space for the data *before* it starts reading, which  means
that it must know how much data the device will send.  However, it  doesn't know
a priori.

Therefore, PyVISA reads from the device in *chunks*.  Each chunk is
20 kilobytes long by default.  If there's still data to be read, PyVISA repeats
the procedure and eventually concatenates the results and returns it to you.
Those 20 kilobytes are large enough so that mostly one read cycle is
sufficient.

The whole thing happens automatically, as you can see.  Normally
you needn't  worry about it.  However, some devices don't like to send data in
chunks.  So  if you have trouble with a certain device and expect data lengths
larger than  the default chunk length, you should increase its value by saying
e.g.   ::

   my_instrument.chunk_size = 102400

This example sets it to 100 kilobytes.


.. _sec:termchars:

Termination characters
----------------------

Somehow the computer must detect when the device is finished with sending a
message.  It does so by using different methods, depending on the bus system.
In most cases you don't need to worry about termination characters because the
defaults are very good.  However, if you have trouble, you may influence
termination characters with PyVISA.

Termination characters may be one character or a sequence of characters.
Whenever this character or sequence
occurs in the input stream, the read  operation is terminated and the read
message is given to the calling  application.  The next read operation continues
with the input stream  immediately after the last termination sequence.  In
PyVISA, the termination  characters are stripped off the message before it is
given to you.

You may set termination characters for each instrument, e.g.

.. code-block:: python

   my_instrument.read_termination = '\r'

('\r' is carriage return, usually appearing in the manuals as CR)

Alternatively you can give it when creating your instrument object::

   my_instrument = rm.open_resource("GPIB::10", read_termination='\r')

The default value depends on the bus system.  Generally, the sequence is empty,
in particular for GPIB. For RS232 it's ``\r``.

You can specify the character to add to each outgoing message using the
``write_termination`` attribute.


`query_delay` and `send_end`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. index::
   single: query_delay
   single: send_end

There are two further options related to message termination, namely
``send_end`` and ``query_delay``.  ``send_end`` is a boolean.  If it's  ``True`` (the
default), the EOI line is asserted after each write operation,  signalling the
end of the operation.  EOI is GPIB-specific but similar action  is taken for
other interfaces.

The argument ``query_delay`` is the time in seconds to wait after
each write  operation.  So you could write::

   my_instrument = rm.open_resource("GPIB::10", send_end=False, delay=1.2)

.. index:: single: EOI line

This will set the delay to 1.2 seconds, and the EOI line is omitted.  By the
way, omitting EOI is *not* recommended, so if you omit it nevertheless, you
should know what you're doing.

