

#include "ast.h"
#include "parser.h"
int main(int argc, char *argv[]){
    const char *source = "return 0;";
    const char *filename = "main.pco";
    AstModule module = parser_parse_module(filename,source);
    return 0;
}
