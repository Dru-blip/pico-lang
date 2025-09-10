#include "pico.h"
#include <stdio.h>

#define DEFINE_FN(name) PICO_LIB_FN(IO_, name)
#define DEFINE_FN_VOID(name) PICO_LIB_FN_VOID(IO_, name)

DEFINE_FN(putchar) {
    pint ch = PICO_POP_INT(env->vm);
    putchar(ch);
    return TO_PICO_INT(ch);
}

DEFINE_FN_VOID(print_int) {
    pint ch = PICO_POP_INT(env->vm);
    printf("%d\n", ch);
}

DEFINE_FN_VOID(puts) {
    pstr str = PICO_POP_STR(env->vm);
    printf("%s\n", str);
}

PICO_EXPORT void pico_lib_Init(pico_env *env) {
    pico_register_native_function(env, "IO_putchar", IO_putchar);
    pico_register_native_void_function(env, "IO_print_int", IO_print_int);
    pico_register_native_void_function(env, "IO_puts", IO_puts);
}
