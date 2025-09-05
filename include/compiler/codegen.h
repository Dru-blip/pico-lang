#pragma once

#include "compiler/irgen.h"
#include <stdio.h>

typedef struct codegen_context {
    BytecodeModule *module;
    FILE *out_file;
} codegen_context_t;

void emit_bytecode(BytecodeModule *module);
