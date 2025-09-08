#include "disassembler.h"
#include "loader.h"
#include "vm.h"

int main(int argc, char *argv[]) {
    bytecode_unit unit = load_bytecode(argv[1]?argv[1]:"../out.pbc");
    // print_bytecode_unit(&unit);
    pico_vm_init(&unit);
    pico_vm_run();
    pico_vm_shutdown();
    return 0;
}
