.phony: clean

libctypes-test.so: ctypes-test.o
	gcc -shared -o libctypes-test.so -Wl,-soname,libctypes-test.so ctypes-test.o

ctypes-test.o: ctypes-test.c
	gcc -fPIC -c ctypes-test.c

clean:
	rm -f ctypes-test.o libctypes-test.so*
