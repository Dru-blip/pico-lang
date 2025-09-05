#pragma once
#include <stdint.h>

typedef struct const_lit ConstLit;
typedef ConstLit* ConstLitRef;
typedef ConstLit* const_lit_list_t;
typedef uint32_t const_lit_index_t ;

typedef enum const_kind {
    CONST_INT,
} ConstKind;

struct const_lit {
    ConstKind kind;
    union {
        int64_t i;
    } value;
};

typedef struct const_pool{
    const_lit_list_t literals;
}ConstPool;


uint32_t cache_int_literal(ConstPool *pool, ConstKind kind, int64_t value);
