.. _contributing:

Contributing to PyVISA
======================

You can contribute in different ways:

Report issues
-------------

You can report any issues with the package, the documentation to the PyVISA `issue tracker`_. Also feel free to submit feature requests, comments or questions. In some cases, platform specific information is required. If you think this is the case, run the following command and paste the output into the issue::

    python -c "from pyvisa import util; util.get_debug_info()"

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


.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _Python: http://www.python.org/
.. _pip: http://www.pip-installer.org/
.. _`Anaconda CE`: https://store.continuum.io/cshop/anaconda
.. _PyPI: https://pypi.python.org/pypi/PyVISA
.. _`National Instruments's VISA`: http://ni.com/visa/
.. _github: http://github.com/hgrecco/pyvisa
.. _`issue tracker`: https://github.com/hgrecco/pyvisa/issues


