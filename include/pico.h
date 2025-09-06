#pragma once

#include <stddef.h>
#include <stdint.h>

#define to_pico_int(value) ((pico_value){.kind = PICO_INT, .i_value = value})
#define to_pico_str(str, len)                                                  \
    ((pico_value){.kind = PICO_STRING, .s_value = str, .size = len})

typedef int32_t pint;
typedef uint8_t pbyte;
typedef uint32_t puint;
typedef int16_t pshort;
typedef char pchar;
typedef char *pstr;
typedef uint64_t pulong;

typedef enum pico_value_kind {
    PICO_INT,
    PICO_STRING,
} pico_value_kind_t;

typedef struct pico_value {
    pico_value_kind_t kind;
    union {
        pint i_value;
        struct {
            puint size;
            pstr s_value;
        };
    };
} pico_value;
