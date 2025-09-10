#include "gc.h"
#include "pico.h"

// TODO: allocate strings on heap and implemente string interning
int main(int argc, char *argv[]) {
    pico_env env;
    pico_env_init(&env);
    pico_load_libraries(&env, argc > 1 ? argv[2] : "../lib/libpio.so");
    bytecode_unit unit = load_bytecode(argv[1] ? argv[1] : "../out.pbc");
    print_bytecode_unit(&unit);
    pico_vm_init(env.vm, &unit);
    pico_vm_run(&env);
    pico_env_deinit(&env);
    return 0;
}
