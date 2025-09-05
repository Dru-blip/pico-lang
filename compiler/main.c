#include "ast.h"
#include "hir.h"
#include "parser.h"

int main(int argc, char *argv[]){
    const char *source = "return 5;";
    const char *filename = "main.pco";
    AstModule module = parser_parse_module(filename,source);
    HirModule hir_module = hir_generate(&module);
    return 0;
}
