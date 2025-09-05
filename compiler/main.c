#include "token.h"
#include "tokenizer.h"
int main(int argc, char *argv[]){
    const token_list tokens=tokenize("def main(){return 0;}");
    print_token_list(tokens);
    return 0;
}
