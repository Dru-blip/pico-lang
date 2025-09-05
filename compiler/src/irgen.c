#include "compiler/irgen.h"
#include "compiler/ast.h"
#include "compiler/hir.h"
#include "compiler/node_iter.h"
#include "compiler/constants.h"
#include "opcode.h"
#include "stb_ds.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct ir_gen_context {
    HirModule *hir_module;
    uint8_t *header;
    uint8_t *const_literals;
    uint8_t *code;
    uint32_t const_count;
} ir_gen_context_t;

static inline HirNodeRef get_hir_node(ir_gen_context_t *ctx, node_index_t idx) {
    return &ctx->hir_module->nodes[idx];
}

static node_index_t hir_iter_get_next(void *nodes, node_index_t idx) {
    return ((hir_node_list_t)nodes)[idx].next;
}

static void int_to_le_bytes(uint32_t value, uint8_t bytes[4]) {
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    bytes[2] = (value >> 16) & 0xFF;
    bytes[3] = (value >> 24) & 0xFF;
}

static void generate_expr(ir_gen_context_t *ctx, node_index_t expr_i) {
    const HirNodeRef expr = get_hir_node(ctx, expr_i);

    switch (expr->kind) {
    case HIR_CONST_LIT: {
        arrput(ctx->code, OP_LIC);
        uint8_t bytes[4];
        int_to_le_bytes(expr->data.const_i, bytes);
        arrput(ctx->code, bytes[0]);
        arrput(ctx->code, bytes[1]);
        break;
    }
    default: {
        printf("Unknown expr kind");
        exit(EXIT_FAILURE);
    }
    }
}

static void generate_return(ir_gen_context_t *ctx, HirNodeRef node) {
    generate_expr(ctx, node->data.expr);
    arrput(ctx->code, OP_RET);
}

static void generate_node(ir_gen_context_t *ctx, HirNodeRef node) {
    switch (node->kind) {
    case AST_RETURN: {
        return generate_return(ctx, node);
    }
    default: {
        printf("Unknown node kind");
        exit(EXIT_FAILURE);
    }
    }
}

static void generate_nodes(ir_gen_context_t *ctx) {
    NodeIter it = node_iter_init(ctx->hir_module->nodes, 0, hir_iter_get_next);
    HirNodeRef node;
    while ((node = node_iter_next(&it)) != nullptr) {
        generate_node(ctx, node);
    }
}

static void generate_constant_literals(ir_gen_context_t *ctx) {
    const uint32_t num_literals = arrlen(ctx->hir_module->const_pool.literals);
    ctx->const_count = num_literals;
    for (uint32_t i = 0; i < num_literals; i++) {
        ConstLitRef lit = &ctx->hir_module->const_pool.literals[i];
        arrput(ctx->const_literals, lit->kind);
        uint8_t buffer[4];
        int_to_le_bytes(lit->value.i, buffer);
        arrput(ctx->const_literals, buffer[0]);
        arrput(ctx->const_literals, buffer[1]);
        arrput(ctx->const_literals, buffer[2]);
        arrput(ctx->const_literals, buffer[3]);
    }
}

BytecodeModule generate_bytecode_module(HirModule *hir_module) {
    ir_gen_context_t ctx = {
        .hir_module = hir_module,
        .code = nullptr,
        .const_literals = nullptr,
        .header = nullptr,
        .const_count = 0,
    };
    generate_constant_literals(&ctx);
    generate_nodes(&ctx);
    return (BytecodeModule){
        .code = ctx.code,
        .const_literals = ctx.const_literals,
        .header = ctx.header,
        .const_count = ctx.const_count,
    };
}
