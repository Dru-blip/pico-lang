#include "compiler/ast.h"

#include "compiler/hir.h"

#include "compiler/parser.h"

//TODO: parse function declarations
int main(int argc, char *argv[]) {
    const char *source = "fn main(){return 5;}";
    const char *filename = "main.pco";
    AstModule module = parser_parse_module(filename, source);
    HirModule hir_module = hir_generate(&module);

    return 0;
}
