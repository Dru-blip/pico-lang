#include "compiler/ast.h"
#include "compiler/codegen.h"
#include "compiler/hir.h"
#include "compiler/irgen.h"
#include "compiler/parser.h"

int main(int argc, char *argv[]) {
    const char *source = "return 5;";
    const char *filename = "main.pco";
    AstModule module = parser_parse_module(filename, source);
    HirModule hir_module = hir_generate(&module);
    BytecodeModule bytecode_module = generate_bytecode_module(&hir_module);
    emit_bytecode(&bytecode_module);
    return 0;
}
