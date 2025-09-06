#pragma once

#include "function.h"
#include "pico.h"

#define PICO_FRAME_NEW(func, stk)                                              \
    (pico_frame){.function = (func), .stack = (stk), .ip = 0}

typedef struct pico_frame {
    pico_function *function;
    pico_value *stack;
    pulong ip;
} pico_frame;
