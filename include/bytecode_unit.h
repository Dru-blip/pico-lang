#include "function.h"
#include "pico.h"
#include <stdint.h>

typedef struct bytecode_unit {
    pico_value *constants;
    pico_function *functions;
    puint main_function_index;
} bytecode_unit;
