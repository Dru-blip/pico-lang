#pragma once

#include <stddef.h>
#include <stdint.h>

#define PICO_TRUE pico_true
#define PICO_FALSE pico_false
#define TO_PICO_INT(value) ((pico_value){.kind = PICO_INT, .i_value = value})
#define TO_PICO_STR(str, len)                                                  \
    ((pico_value){.kind = PICO_STRING, .s_value = str, .size = len})


typedef int32_t pint;
typedef uint8_t pbyte;
typedef uint32_t puint;
typedef int16_t pshort;
typedef char pchar;
typedef char *pstr;
typedef uint64_t pulong;
typedef bool pbool ;


typedef enum pico_value_kind {
    PICO_INT,
    PICO_BOOL,
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
        bool boolean;
    };
} pico_value;

static pico_value pico_true=(pico_value){.kind = PICO_BOOL, .boolean = true};
static pico_value pico_false=(pico_value){.kind = PICO_BOOL, .boolean = false};
