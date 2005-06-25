#include <stdio.h>
#include <string.h>

typedef int (* handler_type)(int* i);

void test_function(handler_type toll) {
  int a;
  a = 5;
  toll(&a);
}
