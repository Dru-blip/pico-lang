#include "gc.h"
#include "pico.h"
#include <stdint.h>

#ifdef DEBUG_BUILD
#include "debugger.h"
#endif

// TODO: allocate strings on heap and implement string interning
// TODO: implement cli for pico runtime.
int main(int argc, char *argv[]) {
    pico_env env;
    pico_env_init(&env);
#ifdef DEBUG_BUILD

#endif
    pico_load_libraries(&env, argc > 1 ? argv[2] : "../lib");
    bytecode_unit unit = load_bytecode(argv[1] ? argv[1] : "../out.pbc");
#ifdef DEBUG_BUILD

#endif
    print_bytecode_unit(&unit);
    pico_vm_init(env.vm, &unit);
    pico_vm_run(&env);
    pico_env_deinit(&env);
    return 0;
}
