#pragma once

#include <stdint.h>

#define to_pico_int(value) ((PicoValue){.kind=PICO_INT, .i_value = value})

typedef int32_t pint;
typedef uint8_t pbyte;

typedef enum pico_value_kind {
    PICO_INT,
} pico_value_kind_t;

typedef struct pico_value {
    pico_value_kind_t kind;
    union {
        pint i_value;
    };
} PicoValue;
