
#include "compiler/codegen.h"
#include "compiler/irgen.h"
#include "stb_ds.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static void int_to_le_bytes(uint32_t value, uint8_t bytes[4]) {
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    bytes[2] = (value >> 16) & 0xFF;
    bytes[3] = (value >> 24) & 0xFF;
}

static void emit_code(codegen_context_t *ctx) {
    fwrite(ctx->module->code, sizeof(uint8_t), arrlen(ctx->module->code),
           ctx->out_file);
}

static void emit_constants(codegen_context_t *ctx) {
    fwrite(ctx->module->const_literals, sizeof(uint8_t),
           arrlen(ctx->module->const_literals), ctx->out_file);
}

static void emit_header(codegen_context_t *ctx) {
    const char magic[] = {'P', 'E', 'X', 'B'};
    const uint8_t version[] = {0x01, 0x00};
    uint8_t buffer[4];
    // emit magic bytes (4B)
    fwrite(magic, sizeof(char), 4, ctx->out_file);
    // emit version (2B)
    fwrite(version, sizeof(uint8_t), 2, ctx->out_file);
    // Padding (2B)
    fwrite((uint8_t[2]){0x00, 0x00}, sizeof(uint8_t), 2, ctx->out_file);
    int_to_le_bytes(0, buffer);
    // Entry point (4B) -> points to main function code
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
    // Constants Count (4B)
    int_to_le_bytes(ctx->module->const_count, buffer);
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
    // Types Count (4B)
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
    // Function Count (4B)
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
    // PADDING (4B)
    int_to_le_bytes(0, buffer);
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
    // CODE LENGTH (4B)
    int_to_le_bytes(arrlen(ctx->module->code), buffer);
    fwrite(buffer, sizeof(uint8_t), 4, ctx->out_file);
}

void emit_bytecode(BytecodeModule *module) {
    codegen_context_t ctx = {
        .module = module,
    };
    FILE *out_file = fopen("output.pbc", "wb");
    if (!out_file) {
        fprintf(stderr, "Failed to open output file\n");
        exit(1);
    }
    ctx.out_file = out_file;
    emit_header(&ctx);
    emit_constants(&ctx);
    emit_code(&ctx);
    fclose(out_file);
}
