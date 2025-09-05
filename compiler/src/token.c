#include "token.h"
#include <stdint.h>
#include <stdio.h>
#include "stb_ds.h"


void print_token(const Token *token) {
    if (!token) {
        printf("NULL token\n");
        return;
    }

    printf("Token { kind: %s, span: { line: %u, col: %u, start: %u, end: %u, line_start_offset: %u }, c_lit: '%c' }\n",
           token_kind_labels[token->kind],
           token->span.line,
           token->span.col,
           token->span.start,
           token->span.end,
           token->span.line_start_offset,
           token->c_lit ? token->c_lit : ' ');
}


void print_token_list(const token_list_t tokens) {
    const uint32_t count=arrlen(tokens);
    printf("Token List (%d tokens):\n", count);
    for (size_t i = 0; i < count; i++) {
        printf("[%zu] ", i);
        print_token(&tokens[i]);
    }
}
