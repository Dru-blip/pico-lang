#pragma once

#include "token.h"
#include <stdint.h>

typedef uint32_t node_index_t;
typedef struct ast_node AstNode;
typedef AstNode *node_list_t;


typedef enum ast_node_kind {
    AST_INT_LIT,
    AST_RETURN,
} AstNodeKind;

struct ast_node {
    AstNodeKind kind;
    token_index_t tok_i;
    node_index_t next; //next sibling
    union {
        node_index_t node_i;
    } data;
};


typedef struct ast_module {
    const char *source;
    const char *filename;
    token_list_t tokens;
    node_list_t nodes;
} AstModule;
