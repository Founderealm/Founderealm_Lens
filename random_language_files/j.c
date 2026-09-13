#include <stdio.h>
#include <stdlib.h>
struct Theta { int id; };
int run(struct Theta t) { return t.id; }
void helper(void) { printf("%d", run((struct Theta){1})); }
