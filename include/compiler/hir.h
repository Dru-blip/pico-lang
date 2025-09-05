#pragma once
#include "ast.h"
#include "constants.h"
#include "token.h"
#include <stdint.h>

typedef struct hir_node HirNode;
typedef HirNode *HirNodeRef;
typedef HirNodeRef hir_node_list_t;
typedef uint32_t node_index_t;

typedef enum hir_node_kind {
    HIR_CONST_LIT,
    HIR_RETURN,
} HirNodeKind;

typedef struct hir_node {
    HirNodeKind kind;
    token_index_t tok_i;
    node_index_t next;
    union {
        const_lit_index_t const_i;
        node_index_t expr;
    } data;
} HirNode;

typedef struct hir_module {
    const char *filename;
    const char *source;
    token_list_t tokens;
    hir_node_list_t nodes;
    ConstPool const_pool;
} HirModule;

HirModule hir_generate(AstModule *ast_module);
