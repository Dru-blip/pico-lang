#include "parser.h"
#include "ast.h"
#include "stb_ds.h"
#include "token.h"
#include "tokenizer.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static inline token_index_t next_token(Parser *parser) {
    return parser->tok_i++;
}

static inline token_index_t parser_advance(Parser *parser) {
    return parser->tok_i + 1 < arrlen(parser->tokens) ? parser->tok_i++
                                                      : parser->tok_i;
}

static inline token_index_t eat_token(Parser *parser, TokenKind kind) {
    return parser->tokens[parser->tok_i].kind == kind ? next_token(parser)
                                                      : UINT32_MAX;
}

static inline token_index_t expect_token(Parser *parser, TokenKind kind) {
    if (parser->tokens[parser->tok_i].kind == kind) {
        return next_token(parser);
    }
    printf("Expected token %d, got %d\n", kind,
           parser->tokens[parser->tok_i].kind);
    exit(EXIT_FAILURE);
}

static inline TokenKind get_token_kind(Parser *parser, token_index_t index) {
    return parser->tokens[index].kind;
}

static node_index_t reserve_node(Parser *parser, AstNodeKind kind,
                                 token_index_t tok_i) {
    const node_index_t index = arrlen(parser->nodes);
    const AstNode node = {
        .kind = kind,
        .tok_i = tok_i,
        .next = UINT32_MAX,
    };
    arrput(parser->nodes, node);
    return index;
}

static node_index_t parse_primary(Parser *parser) {
    const token_index_t tok_i = parser_advance(parser);
    switch (get_token_kind(parser, tok_i)) {
    case TK_INTEGER: {
        return reserve_node(parser, AST_INT_LIT, tok_i);
    }
    default: {
        printf("Unexpected token: %d\n", tok_i);
        exit(EXIT_FAILURE);
    }
    }
}

static node_index_t parse_expr(Parser *parser) { return parse_primary(parser); }

static node_index_t parse_return(Parser *parser) {
    const token_index_t main_tok_i = next_token(parser);
    const node_index_t node_i = reserve_node(parser, AST_RETURN, main_tok_i);
    const node_index_t expr_i = parse_expr(parser);
    parser->nodes[node_i].data.node_i = expr_i;
    expect_token(parser, TK_SEMICOLON);
    return node_i;
}

AstModule parser_parse_module(const char *filename, const char *source) {
    token_list_t tokens = tokenize(source);
    Parser p = {
        .tokens = tokens,
        .filename = filename,
        .source = source,
        .tok_i = 0,
        .nodes = nullptr,
    };
    parse_return(&p);
    return (AstModule){
        .nodes = p.nodes,
        .tokens = tokens,
        .source = source,
        .filename = filename,
    };
}
