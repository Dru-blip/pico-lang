#pragma once
#include <stdint.h>

typedef struct {
  uint32_t line;
  uint32_t col;
  uint32_t start;
  uint32_t end;
  uint32_t line_start_offset;
} Span;

typedef enum {
  TK_CLOSE_PAREN,
  TK_OPEN_BRACE,
  TK_CLOSE_BRACE,

  TK_SEMICOLON,

  TK_OPEN_PAREN,

  TK_INTEGER,
  TK_IDENT,


  TK_KW_DEF,
  TK_KW_RETURN,

  TK_EOF,
} TokenKind;

static const char *token_kind_labels[] = {
    ")", "{", "}", ";", "(", "integer", "ident", "def", "return", "eof"};

typedef struct {
  TokenKind kind;
  Span span;
  char c_lit;
} Token;


typedef Token* token_list;
void print_token_list(const token_list tokens);
