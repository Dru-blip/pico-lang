#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "ast.h"
#include "constants.h"
#include "hir.h"
#include "node_iter.h"
#include "stb_ds.h"
#include "token.h"

typedef struct gen_context {
    const char *filename;
    const char *source;
    ast_node_list_t ast_nodes;
    hir_node_list_t hir_nodes;
    token_list_t tokens;
    ConstPool const_pool;
} Context;

static inline AstNodeRef get_ast_node(Context *ctx, node_index_t idx) {
    return &ctx->ast_nodes[idx];
}

static inline TokenRef get_token(Context *ctx, token_index_t idx) {
    return &ctx->tokens[idx];
}

static node_index_t ast_iter_get_next(void *nodes, node_index_t idx) {
    return ((ast_node_list_t)nodes)[idx].next;
}

static char *extract_token_value(const Context *ctx, const TokenRef token) {
    const size_t len = token->span.end - token->span.start;
    char *buffer = malloc(len + 1);
    if (!buffer) {
        exit(EXIT_FAILURE);
    }
    strncpy(buffer, ctx->source + token->span.start, len);
    buffer[len] = '\0';
    return buffer;
}

static node_index_t reserve_node(Context *ctx, HirNodeKind kind,
                                 token_index_t tok_i) {
    const node_index_t index = arrlen(ctx->hir_nodes);
    const HirNode node = {
        .kind = kind,
        .tok_i = tok_i,
        .next = UINT32_MAX,
    };
    arrput(ctx->hir_nodes, node);
    return index;
}

static node_index_t make_lit_node(Context *ctx, HirNodeKind kind,
                                  token_index_t tok_i,
                                  const_lit_index_t const_i) {
    const node_index_t index = arrlen(ctx->hir_nodes);
    const HirNode node = {
        .kind = kind,
        .tok_i = tok_i,
        .data.const_i = const_i,
    };
    arrput(ctx->hir_nodes, node);
    return index;
}

static node_index_t generate_expr(Context *ctx, node_index_t expr_i) {
    const AstNodeRef expr = get_ast_node(ctx, expr_i);
    switch (expr->kind) {
    case AST_INT_LIT: {
        TokenRef token = get_token(ctx, expr->tok_i);
        char *tok_value = extract_token_value(ctx, token);
        char *endptr;
        const int64_t val = strtoll(tok_value, &endptr, 10);
        const uint32_t const_i =
            cache_int_literal(&ctx->const_pool, CONST_INT, val);
        free(tok_value);
        return make_lit_node(ctx, HIR_CONST_LIT, expr->tok_i, const_i);
    }
    default: {
        printf("Unknown expr kind");
        exit(EXIT_FAILURE);
        break;
    }
    }
}

static node_index_t generate_return(Context *ctx, AstNodeRef node) {
    const node_index_t node_i = reserve_node(ctx, HIR_RETURN, node->tok_i);
    const node_index_t expr_i = generate_expr(ctx, node->data.node_i);
    ctx->hir_nodes[node_i].data.expr = expr_i;
    return node_i;
}

static node_index_t generate_node(Context *ctx, AstNodeRef node) {
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

static void generate_nodes(Context *ctx) {
    NodeIter it = node_iter_init(ctx->ast_nodes, 0, ast_iter_get_next);
    AstNodeRef node;
    while ((node = node_iter_next(&it)) != nullptr) {
        node_index_t node_i = generate_node(ctx, node);
    }
}

HirModule hir_generate(AstModule *ast_module) {
    Context ctx = {.ast_nodes = ast_module->nodes,
                   .source = ast_module->source,
                   .filename = ast_module->filename,
                   .tokens = ast_module->tokens,
                   .hir_nodes = nullptr,
                   .const_pool = {
                       .literals = nullptr,
                   }};
    generate_nodes(&ctx);
    arrfree(ctx.ast_nodes);
    return (HirModule){
        .source = ast_module->source,
        .filename = ast_module->filename,
        .const_pool = ctx.const_pool,
        .nodes = ctx.hir_nodes,
        .tokens = ctx.tokens,
    };
}
