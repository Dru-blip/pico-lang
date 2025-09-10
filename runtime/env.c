#include "gc.h"
#include "pico.h"
#include "stb_ds.h"
#include <dirent.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void pico_env_init(pico_env *env) {
    env->lib_handles = nullptr;
    env->native_functions = nullptr;
    env->vm = malloc(sizeof(pico_vm));
    env->gc = pico_gc_new(1024);
}

void pico_env_deinit(pico_env *env) {
    pico_deinit_libraries(env->lib_handles);
    arrfree(env->lib_handles);
    pico_vm_shutdown(env->vm);
    pico_gc_destroy(env->gc);
    free(env->vm);
}

const bool check_file_ext(const char *filename, const char *ext) {
    const char *dot = strrchr(filename, '.');
    if (!dot || dot == filename)
        return false;
    return strcmp(dot + 1, ext) == 0;
}

void pico_load_libraries(pico_env *env, char *lib_dir_name) {
    DIR *lib_dir = opendir(lib_dir_name);
    if (!lib_dir) {
        fprintf(stderr, "failed to open %s: %s\n", lib_dir_name, strerror(1));
        exit(EXIT_FAILURE);
    }
    char path[256];
    struct dirent *entry;
    while ((entry = readdir(lib_dir))) {
        if (!check_file_ext(entry->d_name, "so"))
            continue;

        snprintf(path, sizeof(path), "%s/%s", lib_dir_name, entry->d_name);
        void *lib_handle = dlopen(path, RTLD_LAZY);

        if (!lib_handle) {
            fprintf(stderr, "Failed to load library %s: %s\n", entry->d_name,
                    dlerror());
            exit(EXIT_FAILURE);
        }

        pico_lib_init init_fn =
            (pico_lib_init)dlsym(lib_handle, "pico_lib_Init");
        if (!init_fn) {
            fprintf(stderr, "Failed to find pico_lib_Init in %s\n",
                    entry->d_name);
            exit(EXIT_FAILURE);
        }

        init_fn(env);
        arrput(env->lib_handles, lib_handle);
    }
}

void pico_deinit_libraries(void **lib_handles) {
    puint count = arrlen(lib_handles);
    for (puint i = 0; i < count; i++) {
        if (lib_handles[i]) {
            dlclose(lib_handles[i]);
        }
    }
}
