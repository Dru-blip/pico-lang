#include "compiler/tokenizer.h"
#include "compiler/token.h"
#include "stb_ds.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


static TokenKind lookup_keyword(const char *ident) {
    for (size_t i = 0; i < sizeof(keywords) / sizeof(keywords[0]); ++i) {
        if (strcmp(keywords[i].key, ident) == 0) {
            return keywords[i].value;
        }
    }
    return TK_IDENT;
}

static inline char current(Tokenizer *t) {
    return (t->pos < t->len) ? t->src[t->pos] : '\0';
}

static inline void advance(Tokenizer *t) {
    t->col++;
    t->pos++;
}

static void skip_whitespace(Tokenizer *t) {
    while (true) {
        char c = current(t);
        if (c == ' ' || c == '\t' || c == '\r') {
            advance(t);
        } else if (c == '\n') {
            t->col = 1;
            t->line++;
            t->pos++;
            t->line_start = t->pos;
        } else {
            break;
        }
    }
}

static Token next_token(Tokenizer *t) {
    skip_whitespace(t);

    Span start = {t->line, t->col, (uint32_t)t->pos, t->pos + 1, t->line_start};

    char c = current(t);
    char val = 0;
    TokenKind kind;

    switch (c) {
    case '\0': {
        advance(t);
        kind = TK_EOF;
        break;
    }
    case '(': {
        advance(t);
        kind = TK_OPEN_PAREN;
        break;
    }
    case ')': {
        advance(t);
        kind = TK_CLOSE_PAREN;
        break;
    }
    case '{': {
        advance(t);
        kind = TK_OPEN_BRACE;
        break;
    }
    case '}': {
        advance(t);
        kind = TK_CLOSE_BRACE;
        break;
    }
    case ';': {
        advance(t);
        kind = TK_SEMICOLON;
        break;
    }
    default:
        if (isdigit(c)) {
            while (isdigit(current(t))) {
                advance(t);
            }
            kind = TK_INTEGER;
        } else if (isalpha(c) || c == '_') {
            size_t start_pos = t->pos;
            while (isalnum(current(t)) || current(t) == '_')
                advance(t);
            size_t len = t->pos - start_pos;
            char *dup = strndup(t->src + start_pos, len);
            kind = lookup_keyword(dup);
            free(dup);
        } else {
            printf("unexpected character '%c'\n", c);
            exit(1);
        }
    }
    start.end = t->pos;
    return (Token){
        .kind = kind,
        .span = start,
        .c_lit = val,
    };
}

token_list_t tokenize(const char *source) {
    Tokenizer tokenizer = {
        .src = source,
        .len = strlen(source),
        .pos = 0,
        .line = 1,
        .col = 1,
        .line_start = 0,
    };

    Token *tokens = nullptr;

    while (tokenizer.pos <= tokenizer.len) {
        const Token tok = next_token(&tokenizer);
        arrput(tokens, tok);
    }

    return tokens;
}
