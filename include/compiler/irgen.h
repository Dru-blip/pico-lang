#pragma once

#include "hir.h"
#include <stdint.h>
#include <sys/types.h>

typedef struct bytecode_module {
    uint8_t *header;
    uint8_t *const_literals;
    uint8_t *code;
    uint32_t const_count;
} BytecodeModule;

BytecodeModule generate_bytecode_module(HirModule *hir_module);
