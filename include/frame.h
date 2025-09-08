#pragma once

#include "function.h"
#include "pico.h"

#define PICO_FRAME_NEW(func, stk,parent_frame)                                              \
    (pico_frame) {                                                             \
        .function = (func), .stack = (stk), .ip = 0,                           \
        .locals = calloc((func)->local_count, sizeof(pico_value)),             \
        .parent = parent_frame                                                 \
    }

#define PICO_FRAME_DEINIT(frame)                                               \
    do {                                                                       \
        free((frame).locals);                                                  \
        (frame).locals = NULL;                                                 \
    } while (0)

typedef struct pico_frame {
    pico_function *function;
    pico_value *stack;
    pico_value *locals;
    pulong ip;
    struct pico_frame *parent;
} pico_frame;
