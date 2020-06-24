.. _intro-event_handling:

Event handling
==============

.. include:: ../substitutions.sub

VISA supports generating events on the instrument side usually when a register
change and handling then on the controller using two different mechanisms:
- storing the events in a queue
- calling a dedicated handler function registered for that purpose when the
event occurs

PyVISA supports using both mechanism and tries to provide a convenient interface
to both. Below we give a couple of example of how to use each mechanism (using
a fictional instrument).

Waiting on events using a queue
-------------------------------

First let's have a look at how to wait for an event to occur which will be stored
in a queue.

.. code-block:: python

    from pyvisa import ResourceManager, constants

    rm = ResourceManager

    with rm.open_resource("TCPIP::192.168.0.2::INSTR") as instr:

        # Type of event we want to be notified about
        event_type = constants.EventType.service_request
        # Mechanism by which we want to be notified
        event_mech = constants.EventMechanism.queue

        instr.enable_event(event_type, event_mech)

        # Instrument specific code to enable service request
        # (for example on operation complete OPC)
        instr.write("*SRE 1")
        instr.write("INIT")

        # Wait for the event to occur
        response = instr.wait_on_event(event_type, 1000)
        assert response.event.event_type == event_type
        assert response.timed_out = False
        instr.disable_event(event_type, event_mech)

Let's examine the code. First, to avoid repeating ourselves, we store the type
of event we want to be notified about and the mechanism we want to use to be notified.
And we enable event notifications.

.. code:: python

    # Type of event we want to be notified about
    event_type = constants.EventType.service_request
    # Mechanism by which we want to be notified
    event_mech = constants.EventMechanism.queue

    instr.enable_event(event_type, event_mech)


Next we need to setup our instrument to generate the kind of event at the right
time and start the operation that will lead to the event. For the sake of that
example we are going to consider a Service Request event. Usually service request
can be enabled for a range of register state, the details depending on the
instrument. One useful case is to generate a service request when an operation
is complete which is we are pretending to do here.

Finally we wait for the event to occur and we specify a timeout of 1000ms to
avoid waiting for ever. Once we received the event we disable event handling.


Registering handlers for event
------------------------------

Rather than waiting for an event, it can sometimes be convenient to take immediate
action when an event occurs, in which having the VISA library call directly a function
can be useful. Let see how.

.. note::

    One can enable event handling using both mechanisms (constants.EventMechanism.all)

.. code-block:: python

    from time import sleep
    from pyvisa import ResourceManager, constants

    rm = ResourceManager

    def handle_event(resource, event, user_handle):
        resource.called = True
        print(f"Handled event {event.event_type} on {resource}")

    with rm.open_resource("TCPIP::192.168.0.2::INSTR") as instr:

        instr.called = False

        # Type of event we want to be notified about
        event_type = constants.EventType.service_request
        # Mechanism by which we want to be notified
        event_mech = constants.EventMechanism.queue

        wrapped = instr.wrap_handler(handle_event)

        user_handle = instr.install_handler(event_type, wrapped, 42)
        instr.enable_event(event_type, event_mech, None)

        # Instrument specific code to enable service request
        # (for example on operation complete OPC)
        instr.write("*SRE 1")
        instr.write("INIT")

        while not instr.called:
            sleep(10)

        instr.disable_event(event_type, event_mech)
        instr.uninstall_handler(event_type, wrapped, user_handle)

Our handler function needs to have a specific signature to be used by VISA. The
expected signature is (session, event_type, event_context, user_handle). This
signature is not exactly convenient since it forces us to deal with a number of
low-level details such session (ID of a resource in VISA) and event_context that
serves the same purpose for events. One way to get a nicer interface is to wrap
the handler using the |wrap_handler| method of the |Resource| object. The wrapped
function is expected to have the following signature: (resource, event, user_handle)
which the signature of our handler:

.. code:: python

    def handle_event(resource, event, user_handle):
        resource.called = True
        print(f"Handled event {event.event_type} on {resource}")

And before installing the handler, we wrap it:

.. code:: python

    wrapped = instr.wrap_handler(handle_event)

When wrapping a handler, you need to use the resource on which it is going to be
installed to wrap it. Furthermore note that in order to uninstall a handler you
need to keep the wrapped version around.

Next we install the handler and enable the event processing:

.. code:: python

    user_handle = instr.install_handler(event_type, wrapped, 42)
    instr.enable_event(event_type, event_mech, None)

When installing a handler one can optionally, specify a user handle that will be
passed to the handler. This handle can be used to identify which handler is called
when registering the same handler multiple times on the same resource. That value
may have to be converted by the backend. As a consequence the value passed to
the handler may not the same as the value registered and its value will be to
the backend dependent. For this reason you need to keep the converted value
returned by install handler to uninstall the handler at a later time.

.. note::

    In the case of ctwrapper that ships with PyVISA, the value is converted
    to an equivalent ctypes object (c_float for a float, c_int for an integer, etc)
