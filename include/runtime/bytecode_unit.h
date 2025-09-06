#include "pico.h"
#include <stdint.h>

typedef struct bytecode_unit {
    pbyte *header;
    PicoValue* constants;
    pbyte *code;
} BytecodeUnit;
