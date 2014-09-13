.. _getting:

Installation
============

PyVISA is a frontend to the VISA library. It runs on Python 2.6+ and 3.2+.

You can install it using pip_::

    $ pip install -U pyvisa


NI Backend
----------

In order for PyVISA to work, you need to have a suitable backend. PyVISA includes
a backend that wraps the `National Instruments's VISA`_ library. However, you need to download
and install the library yourself (See :ref:`getting_nivisa`). There are multiple
VISA implementations from different vendors. PyVISA is tested only against
`National Instruments's VISA`_.

.. warning:: PyVISA works with 32- and 64- bit Python and can deal with 32- and 64-bit VISA libraries without any extra configuration. What PyVISA cannot do is open a 32-bit VISA library while running in 64-bit Python (or the other way around).

   **You need to make sure that the Python and VISA library have the same bitness**


Testing your installation
-------------------------


That's all! You can check that PyVISA is correctly installed by starting up python, and creating a ResourceManager:

    >>> import visa
    >>> rm = visa.ResourceManager()
    >>> print(rm.list_resources())

If you encounter any problem, take a look at the :ref:`faq`. There you will find the
solutions to common problem as well as useful debugging techniques. If everything fails,
feel free to open an issue in our `issue tracker`_


Using the development version
-----------------------------

You can install the latest development version (at your own risk) directly form GitHub_::

    $ pip install -U https://github.com/hgrecco/pyvisa/zipball/master


.. note:: If you have an old system installation of Python and you don't want to
   mess with it, you can try `Anaconda CE`_. It is a free Python distribution by
   Continuum Analytics that includes many scientific packages.


.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _Python: http://www.python.org/
.. _pip: http://www.pip-installer.org/
.. _`Anaconda CE`: https://store.continuum.io/cshop/anaconda
.. _PyPI: https://pypi.python.org/pypi/PyVISA
.. _GitHub: https://github.com/hgrecco/pyvisa
.. _`National Instruments's VISA`: http://ni.com/visa/
.. _`issue tracker`: https://github.com/hgrecco/pyvisa/issues
