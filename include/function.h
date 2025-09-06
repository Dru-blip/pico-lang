#pragma once

#include "pico.h"

typedef struct pico_function {
    puint name_id;
    pbyte *code;
    pulong code_len;
} pico_function;
