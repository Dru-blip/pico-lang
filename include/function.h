#pragma once

#include "pico.h"

typedef struct pico_function {
    puint name_id;
    pbyte *code;
    puint local_count;
    puint param_count;
    pulong code_len;
} pico_function;
