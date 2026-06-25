.. _advanced-testing-harness:

Shared Backend Test Harness
===========================

PyVISA ships a shared pytest harness for backend contract tests in
``pyvisa.testing``. The harness lets backend maintainers reuse the same tests
across multiple backends, and it also lets users run those tests against their
own hardware resources.

The shared contracts currently live in ``pyvisa/testing/contracts``.

The harness is built around three concepts:

- a resource-manager provider chooses how ``ResourceManager`` instances are created.
- an instrument profile names the logical resources and capability flags for a test target.
- an instrument pool exposes resource-class-specific commands while keeping the
    shared contracts backend-agnostic.

When to use this harness
------------------------

Use the shared harness when you want to:

- validate an alternative backend against the common PyVISA contract tests.
- run contract tests on a specific backend with specific hardware addresses.
- keep backend-specific skips/xfails centralized by contract identifier.

Backend selection
-----------------

Contract tests do not hard-code a backend. The shared plugin resolves a
``ResourceManagerProvider`` first and then creates ``ResourceManager``
instances through that provider.

The default provider behaves as follows:

- ``--pyvisa-backend-id=ivi`` selects the built-in IVI provider.
- any other backend id falls back to normal PyVISA backend resolution.
- backend repositories can override the provider entirely through
    ``pytest_pyvisa_select_resource_manager_provider``.

For backend ids that use normal PyVISA resolution, select the backend exactly
as in normal PyVISA usage:

- with ``PYVISA_LIBRARY`` (recommended in CI):

  .. code-block:: bash

      export PYVISA_LIBRARY=@py

- or in a test session for your backend, for example in ``tests/conftest.py``:

  .. code-block:: python

      import os
      os.environ.setdefault("PYVISA_LIBRARY", "@mybackend")

The harness also accepts a logical backend id through pytest:

.. code-block:: bash

    pytest --pyvisa-backend-id=mybackend

``--pyvisa-backend-id`` is used by hook implementations to expose
capabilities/exclusions and provider selection. It does not replace
``PYVISA_LIBRARY`` for backends that still use normal PyVISA backend
resolution.

To force the IVI provider to use a specific vendor library, pass
``--pyvisa-ivi-library``:

.. code-block:: bash

    pytest pyvisa/testing/contracts --pyvisa-backend-id=ivi --pyvisa-ivi-library=/path/to/visa64.dll

This is useful when you want the shared harness to ignore any ambient
``PYVISA_LIBRARY`` setting and always open the IVI backend through a specific
library path.

Using the standard harness with a different backend
---------------------------------------------------

The standard harness can be reused unchanged from either the PyVISA repository
or a backend repository.

Run the shared contracts from the PyVISA repository against ``pyvisa-py``:

.. code-block:: bash

    export PYVISA_LIBRARY=@py
    pytest pyvisa/testing/contracts --pyvisa-backend-id=py

Run the shared contracts from the ``pyvisa-py`` repository through its wrapper
module:

.. code-block:: bash

    pytest tests/keysight_assisted_tests/test_shared_contracts.py --pyvisa-backend-id=py

In both cases the backend repository can still override provider and pool
selection in its own ``tests/conftest.py``.

Using the harness from another backend project
----------------------------------------------

In your backend repository, enable the plugin and implement the hooks you need.

1. Load the shared plugin:

   .. code-block:: python

      # tests/conftest.py
      pytest_plugins = ("pyvisa.testing.pytest_plugin",)

2. Provide a profile (resource addresses, commands, capabilities):

   .. code-block:: python

      import pytest
      from pyvisa.testing import InstrumentProfile

      @pytest.hookimpl(tryfirst=True)
      def pytest_pyvisa_select_profile(config, profile_name):
          return InstrumentProfile(
              name="lab-rig",
              resource_addresses={
                  "TCPIP::INSTR": "TCPIP::192.168.1.50::inst0::INSTR",
                  "TCPIP::SOCKET": "TCPIP::192.168.1.50::5025::SOCKET",
              },
              command_map={
                  "identity_query": "*IDN?",
                  "shared_query": "QUERY?",
              },
              capabilities={
                  "transport.vxi11": True,
                  "transport.socket": True,
                  "transport.hislip": False,
              },
          )

   Profiles describe the hardware target. Providers describe the backend.
   Keep those responsibilities separate so the same profile can be reused with
   different backends.

3. Optionally provide an explicit resource-manager provider:

   .. code-block:: python

      from pyvisa.testing import StaticResourceManagerProvider

      @pytest.hookimpl(tryfirst=True)
      def pytest_pyvisa_select_resource_manager_provider(config, backend_id, profile):
          if backend_id != "mybackend":
              return None
          return StaticResourceManagerProvider(
              name="mybackend",
              backend_id="mybackend",
              specification="@mybackend",
              backend_capabilities={"transport.vxi11": True},
              ignores_standard_env=True,
          )

4. Optionally declare exclusions by contract id:

   .. code-block:: python

      @pytest.hookimpl(tryfirst=True)
      def pytest_pyvisa_contract_exclusions(config, backend_id, profile):
          if backend_id != "mybackend":
              return []
          return [
              ("identity.query.tcpip::hislip", "HiSLIP not supported"),
          ]

5. Run shared contracts:

   .. code-block:: bash

      pytest tests/test_shared_contracts.py --pyvisa-backend-id=mybackend

Running on a specific backend and specific hardware resources
--------------------------------------------------------------

The default profile provider reads ``PYVISA_TESTER_*`` variables and files
through ``pyvisa.testing.env_profile``.

Create a profile file (for example ``pyvisa_tester.env``):

.. code-block:: ini

    PYVISA_TESTER_ASSISTED=1

    PYVISA_TESTER_VXI11=1
    PYVISA_TESTER_HISLIP=0
    PYVISA_TESTER_SOCKET=1
    PYVISA_TESTER_USB=1

    PYVISA_TESTER_VXI11_ADDR=TCPIP::192.168.1.50::inst0::INSTR
    PYVISA_TESTER_SOCKET_ADDR=TCPIP::192.168.1.50::5025::SOCKET
    PYVISA_TESTER_USB_INSTR_ADDR=USB0::0xF4EC::0xEE3A::PYVISA0001::INSTR

    PYVISA_TESTER_CMD_ERROR_QUERY=SYST:ERR?
    PYVISA_TESTER_CMD_BINARY_CONFIGURE_TEMPLATE=DATA:BIN:CFG {datatype},{count},{endian},{header},{termination},{pattern},{start}
    PYVISA_TESTER_CMD_BINARY_READ_QUERY=DATA:BIN:READ?

    PYVISA_TESTER_EXPECTED_IDN=ACME,Model 1000,123456,1.0

Then run with an explicit backend and profile source:

.. code-block:: bash

    export PYVISA_LIBRARY=@mybackend
    export PYVISA_TESTER_ENV_FILE=/path/to/pyvisa_tester.env
    pytest pyvisa/testing/contracts --pyvisa-backend-id=mybackend --pyvisa-profile=env

You can use the same env-backed profile with different backends. For example,
to exercise the IVI backend against the same hardware target:

.. code-block:: bash

    pytest pyvisa/testing/contracts --pyvisa-backend-id=ivi --pyvisa-profile=env --pyvisa-ivi-library=/path/to/visa64.dll

To exercise ``pyvisa-py`` against the same target:

.. code-block:: bash

    export PYVISA_LIBRARY=@py
    pytest pyvisa/testing/contracts --pyvisa-backend-id=py --pyvisa-profile=env

Notes:

- ``--pyvisa-profile=env`` is the default and can be omitted.
- If ``PYVISA_TESTER_ASSISTED`` is not ``1``, hardware contract tests are skipped.
- Capability flags such as ``PYVISA_TESTER_HISLIP=0`` disable only the matching
  contract slices; they do not affect the other resources in the same profile.
- You can still override profile selection by implementing
  ``pytest_pyvisa_select_profile`` in your own ``conftest.py``.

Assisted test modules can also rely on fixture-level profile checks instead of
import-time environment markers. In the PyVISA tree, the
``tests/pyvisa_tester_assisted_tests/conftest.py`` module exposes:

- ``require_pyvisa_tester_profile`` to ensure the selected profile targets the
    pyvisa-tester stack.
- ``require_assisted_resource(resource_key)`` to apply capability checks and
    resolve resource addresses consistently from the selected profile.

This keeps transport selection and skip behavior in one place and avoids
duplicating environment-dependent marker logic per test module.

Capability-gated non-message stubs
----------------------------------

The shared contracts include capability-gated stubs in
``pyvisa/testing/contracts/test_resource_capability_stubs.py``. These stubs are
intended to reserve contract identifiers and provide a migration path from
"declared but untested" capabilities to strict behavior checks.

Current stub families include:

- resource locking (``resource.stub.locking.*``)
- trigger/clear and status-byte contracts (``resource.stub.trigger_clear.*``,
    ``resource.stub.status_byte.*``)
- SRQ queue/handler event paths (``resource.stub.event.queue.*``,
    ``resource.stub.event.handler.*``)
- USB control-transfer and USB attribute slices
    (``resource.stub.usb.control_transfer.usb::instr``,
    ``resource.stub.usb.attributes.usb::instr``)
- GPIB INTFC bus-control/controller-operation slices
    (``resource.stub.gpib.intfc.bus_control``,
    ``resource.stub.gpib.intfc.controller_ops``)

These stubs are driven by capability keys (for example
``resource.usb.control_transfer``, ``resource.usb.attributes``,
``resource.gpib.intfc.controller_ops``) so backend/profile owners can enable
them incrementally.

Running one backend against one resource class
----------------------------------------------

Use normal pytest path selection together with the backend/profile options to
focus on a single contract module or transport slice.

Run only the identity contracts for one backend:

.. code-block:: bash

    pytest pyvisa/testing/contracts/test_identity_contract.py --pyvisa-backend-id=py --pyvisa-profile=env

Run the binary contracts only:

.. code-block:: bash

    pytest pyvisa/testing/contracts/test_binary_value_contracts.py --pyvisa-backend-id=ivi --pyvisa-profile=env --pyvisa-ivi-library=/path/to/visa64.dll

If a resource class should be excluded for a given run, prefer turning off the
matching capability in the selected profile instead of branching inside the
shared contracts.

Useful test selection patterns
------------------------------

Run only shared contracts:

.. code-block:: bash

    pytest -m pyvisa_contract

Run only hardware-dependent contracts:

.. code-block:: bash

    pytest -m pyvisa_hardware

Run one contract module:

.. code-block:: bash

    pytest pyvisa/testing/contracts/test_identity_contract.py
