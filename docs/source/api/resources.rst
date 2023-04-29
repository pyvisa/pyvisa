.. _api_resources:

Resource classes
----------------

Resources are high level abstractions to managing specific sessions. An instance
of one of these classes is returned by the :meth:`~pyvisa.highlevel.ResourceManager.open_resource`
depending on the resource type.

Generic classes
~~~~~~~~~~~~~~~

    - :class:`~pyvisa.resources.Resource`
    - :class:`~pyvisa.resources.MessageBasedResource`
    - :class:`~pyvisa.resources.RegisterBasedResource`


Specific Classes
~~~~~~~~~~~~~~~~

    - :class:`~pyvisa.resources.SerialInstrument`
    - :class:`~pyvisa.resources.TCPIPInstrument`
    - :class:`~pyvisa.resources.TCPIPSocket`
    - :class:`~pyvisa.resources.USBInstrument`
    - :class:`~pyvisa.resources.USBRaw`
    - :class:`~pyvisa.resources.GPIBInstrument`
    - :class:`~pyvisa.resources.GPIBInterface`
    - :class:`~pyvisa.resources.FirewireInstrument`
    - :class:`~pyvisa.resources.PXIInstrument`
    - :class:`~pyvisa.resources.PXIInstrument`
    - :class:`~pyvisa.resources.VXIInstrument`
    - :class:`~pyvisa.resources.VXIMemory`
    - :class:`~pyvisa.resources.VXIBackplane`

.. currentmodule::`pyvisa.resources`


.. autoclass:: pyvisa.resources.Resource
    :members:
    :inherited-members:
    :undoc-members:


.. autoclass:: pyvisa.resources.MessageBasedResource
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:


.. autoclass:: pyvisa.resources.RegisterBasedResource
    :members:
    :inherited-members:
    :undoc-members:


.. autoclass:: pyvisa.resources.SerialInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:


.. autoclass:: pyvisa.resources.TCPIPInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.TCPIPSocket
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.USBInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.USBRaw
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.GPIBInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.GPIBInterface
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.FirewireInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.PXIInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.PXIMemory
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.VXIInstrument
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.VXIMemory
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

.. autoclass:: pyvisa.resources.VXIBackplane
    :members:
    :inherited-members:
    :exclude-members: ask_delay, ask_for_values, ask
    :undoc-members:

