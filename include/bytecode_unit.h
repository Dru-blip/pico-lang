#include "function.h"
#include "pico.h"
#include <stdint.h>

typedef struct bytecode_unit {
    pico_value *constants;
    pico_function *functions;
} bytecode_unit;
