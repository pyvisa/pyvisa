.PHONY: all upload

all: vpp43.html index.html pyvisa.pdf pyvisa

vpp43.html: vpp43.txt
	rst2html.py vpp43.txt > vpp43.html

index.html: homepage.txt
	rst2html.py homepage.txt > index.html

pyvisa.pdf: pyvisa.tex
	rm -Rf pyvisa
	mkhowto --html --pdf --up-link http://pyvisa.sourceforge.net \
	  --up-title "PyVISA homepage" pyvisa.tex

upload:
	scp vpp43.html index.html default.css pyvisa.pdf \
	  shell.sf.net:/home/groups/p/py/pyvisa/htdocs/
	scp -r pyvisa/* shell.sf.net:/home/groups/p/py/pyvisa/htdocs/pyvisa/
