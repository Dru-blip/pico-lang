
#include "compiler/constants.h"
#include <stdint.h>

#include "stb_ds.h"

uint32_t cache_int_literal(ConstPool *pool, ConstKind kind, int64_t value) {
    const uint32_t len = arrlen(pool->literals);
    for (uint32_t i = 0; i < len; i++) {
        ConstLitRef lit = &pool->literals[i];
        if (lit->value.i == value) {
            return i;
        }
    }

    const uint32_t lit_i = arrlen(pool->literals);
    ConstLit lit = {
        .kind = CONST_INT,
        .value.i = value,
    };
    arrput(pool->literals, lit);
    return lit_i;
}
