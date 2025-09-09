#include "pico.h"
#include <stdio.h>

#define IO_FN(name) IO_##name

PICO_EXPORT pico_value IO_FN(putchar)(pico_env *env, pico_value *args) {
    pint ch = AS_INT(args);
    putchar(ch);
    return TO_PICO_INT(ch);
}

PICO_EXPORT pico_value IO_FN(print_int)(pico_env *env, pico_value *args) {
    pint ch = AS_INT(args);
    printf("%d\n", ch);
    return TO_PICO_INT(ch);
}

PICO_EXPORT void pico_lib_Init(pico_env *env) {
    pico_register_native_function(env, "IO_putchar", IO_putchar);
    pico_register_native_function(env, "IO_print_int", IO_print_int);
}
