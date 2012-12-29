python setup.py build_sphinx -aE
rsync -avz doc/_build/html/* bauflo3,pyvisa@web.sourceforge.net:htdocs
