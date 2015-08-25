.. _contributing:

Contributing to PyVISA
======================

You can contribute in different ways:

Report issues
-------------

You can report any issues with the package, the documentation to the PyVISA `issue tracker`_. Also feel free to submit feature requests, comments or questions. In some cases, platform specific information is required. If you think this is the case, run the following command and paste the output into the issue::

    python -m visa info

It is useful that you also provide the log output. To obtain it, add the following lines to your code::

    import visa
    visa.log_to_screen()


Contribute code
---------------

To contribute fixes, code or documentation to PyVISA, send us a patch, or fork PyVISA in github_ and submit the changes using a pull request.

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


Contributing to an existing backend
-----------------------------------

Backends are the central piece of PyVISA as they provide the low level communication
over the different interfaces. There a couple of backends in the wild which can use
your help. Look them up in PyPI_ (try `pyvisa``` in the search box) and see where you
can help.


Contributing a new backend
--------------------------

If you think there is a new way that low level communication can be achieved, go for
it. You can use any of the existing backends as a template or start a thread in the
`issue tracker`_ and we will be happy to help you.




.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _Python: http://www.python.org/
.. _pip: http://www.pip-installer.org/
.. _`Anaconda CE`: https://store.continuum.io/cshop/anaconda
.. _PyPI: https://pypi.python.org/pypi/PyVISA
.. _`National Instruments's VISA`: http://ni.com/visa/
.. _github: http://github.com/hgrecco/pyvisa
.. _`issue tracker`: https://github.com/hgrecco/pyvisa/issues


