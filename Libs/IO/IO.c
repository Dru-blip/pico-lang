#include "pico.h"
#include <stdio.h>

#define DEFINE_FN(name) PICO_LIB_FN(IO_, name)
#define DEFINE_FN_VOID(name) PICO_LIB_FN_VOID(IO_, name)

DEFINE_FN(putchar) {
    pint ch = GET_ARG_INT(args, 0);
    putchar(ch);
    return TO_PICO_INT(ch);
}

DEFINE_FN_VOID(print_int) {
    pint ch = GET_ARG_INT(args, 0);
    printf("%d\n", ch);
}

DEFINE_FN_VOID(puts) {
    pstr str = GET_ARG_STR(args, 0);
    printf("%s\n", str);
}

PICO_EXPORT void pico_lib_Init(pico_env *env) {
    pico_register_native_function(env, "IO_putchar", 1, IO_putchar);
    pico_register_native_void_function(env, "IO_print_int", 1, IO_print_int);
    pico_register_native_void_function(env, "IO_puts", 1, IO_puts);
}
