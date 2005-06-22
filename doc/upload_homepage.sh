#! /bin/sh

rst2html.py vpp43.txt > vpp43.html
rst2html.py homepage.txt > index.html
rm -Rf pyvisa
mkhowto --html --pdf --up-link http://pyvisa.sourceforge.net --up-title "PyVISA homepage" pyvisa.tex

scp vpp43.html index.html default.css pyvisa.pdf shell.sf.net:/home/groups/p/py/pyvisa/htdocs/
scp -r pyvisa/* shell.sf.net:/home/groups/p/py/pyvisa/htdocs/pyvisa/
