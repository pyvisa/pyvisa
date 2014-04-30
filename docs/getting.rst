.. _getting:

Installation
============

PyVISA is a wrapper around the `National Instruments's VISA` library, which you need to download and install in order to use PyVISA (:ref:`getting_nivisa`).

PyVISA has no additional dependencies except Python_ itself. In runs on Python 2.6+ and 3.2+.

.. warning:: PyVISA works with 32- and 64- bit Python and can deal with 32- and 64-bit VISA libraries without any extra configuration. What PyVISA cannot do is open a 32-bit VISA library while running in 64-bit Python (or the other way around).

   **You need to make sure that the Python and VISA library have the same bitness**

You can install it using pip_::

    $ pip install pyvisa

or using easy_install_::

    $ easy_install pyvisa

That's all! You can check that PyVISA is correctly installed by starting up python, and importing PyVISA:

    >>> import visa
    >>> lib = visa.VisaLibrary()

If you encounter any problem, take a look at the :ref:`faq`.


Getting the code
----------------

You can also get the code from PyPI_ or GitHub_. You can either clone the public repository::

    $ git clone git://github.com/hgrecco/pyvisa.git

Download the tarball::

    $ curl -OL https://github.com/hgrecco/pyvisa/tarball/master

Or, download the zipball::

    $ curl -OL https://github.com/hgrecco/pyvisa/zipball/master

Once you have a copy of the source, you can embed it in your Python package, or install it into your site-packages easily::

    $ python setup.py install


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
