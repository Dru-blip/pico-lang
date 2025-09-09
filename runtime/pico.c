#include "pico.h"

#include "stb_ds.h"
#include "uthash.h"
#include <stdio.h>


// void pico_register_native_function(pico_env *env, const char *name,
//                                    pico_native_fn handle) {

//     native_fn_entry entry = {.handle = handle, .name = name};
//     HASH_ADD_KEYPTR(hh, env->native_functions, entry.name, strlen(entry.name),
//                     &entry);
//     printf("Registered native function: %s\n", entry.name);
// }
