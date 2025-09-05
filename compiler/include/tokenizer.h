#pragma once
#include <stddef.h>
#include <stdint.h>

#include "token.h"

typedef struct {
  const char *src;
  size_t len;
  size_t pos;
  uint32_t line;
  uint32_t col;
  uint32_t line_start;
} Tokenizer;

typedef struct {
  const char *key;
  TokenKind value;
} Keyword;

static Keyword keywords[] = {
    {"def", TK_KW_DEF},
    {"return", TK_KW_RETURN},
};

token_list tokenize(const char *source);
