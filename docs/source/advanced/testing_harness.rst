.. _advanced-testing-harness:

Shared Backend Test Harness
===========================

PyVISA ships a shared pytest harness for backend contract tests in
``pyvisa.testing``. The harness lets backend maintainers reuse the same tests
across multiple backends, and it also lets users run those tests against their
own hardware resources.

The shared contracts currently live in ``pyvisa/testing/contracts``.

When to use this harness
------------------------

Use the shared harness when you want to:

- validate an alternative backend against the common PyVISA contract tests.
- run contract tests on a specific backend with specific hardware addresses.
- keep backend-specific skips/xfails centralized by contract identifier.

Backend selection
-----------------

Contract tests instantiate ``pyvisa.ResourceManager()`` without a hard-coded
backend. Select the backend exactly as in normal PyVISA usage:

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
capabilities/exclusions. It does not replace ``PYVISA_LIBRARY``.

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

3. Optionally declare exclusions by contract id:

   .. code-block:: python

      @pytest.hookimpl(tryfirst=True)
      def pytest_pyvisa_contract_exclusions(config, backend_id, profile):
          if backend_id != "mybackend":
              return []
          return [
              ("identity.query.tcpip::hislip", "HiSLIP not supported"),
          ]

4. Run shared contracts:

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

    PYVISA_TESTER_VXI11_ADDR=TCPIP::192.168.1.50::inst0::INSTR
    PYVISA_TESTER_SOCKET_ADDR=TCPIP::192.168.1.50::5025::SOCKET
    PYVISA_TESTER_EXPECTED_IDN=ACME,Model 1000,123456,1.0

Then run with an explicit backend and profile source:

.. code-block:: bash

    export PYVISA_LIBRARY=@mybackend
    export PYVISA_TESTER_ENV_FILE=/path/to/pyvisa_tester.env
    pytest pyvisa/testing/contracts --pyvisa-backend-id=mybackend --pyvisa-profile=env

Notes:

- ``--pyvisa-profile=env`` is the default and can be omitted.
- If ``PYVISA_TESTER_ASSISTED`` is not ``1``, hardware contract tests are skipped.
- You can still override profile selection by implementing
  ``pytest_pyvisa_select_profile`` in your own ``conftest.py``.

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
