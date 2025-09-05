#pragma once

#include "ast.h"
#include "token.h"

typedef struct parser {
    const char *source;
    const char *filename;
    token_list_t tokens;
    uint32_t tok_i;
    ast_node_list_t nodes;
} Parser;

AstModule parser_parse_module(const char *filename, const char *source);
