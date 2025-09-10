#pragma once

#include "gc.h"
#include "uthash.h"
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define GLUE(a, b) a##b
#define FUNC_NAME(prefix, name) GLUE(prefix, name)
#define DEF_LIB_FUNC(ret, name, ...)                                           \
    ret FUNC_NAME(LIB_PREFIX, name)(__VA_ARGS__)

#define PICO_TRUE pico_true
#define PICO_FALSE pico_false
#define TO_PICO_INT(value) ((pico_value){.kind = PICO_INT, .i_value = value})
#define TO_PICO_STR(str, len)                                                  \
    ((pico_value){.kind = PICO_STRING, .s_value = str, .size = len})

#define TO_PICO_OBJ(obj_ptr)                                                   \
    ((pico_value){.kind = PICO_OBJECT, .objref = (obj_ptr)})

#define AS_OBJ(pico_val) ((pico_val)->objref)

#define AS_INT(pico_value) ((pico_value)->i_value)
#define AS_STR(pico_value) ((pico_value)->s_value)

#define PICO_POP_INT(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].i_value)
#define PICO_POP_STR(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].s_value)
#define PICO_POP_OBJ(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].objref)

#define PICO_OBJ_FIELD_PTR(obj, index) (&((obj)->fields[index]))
#define PICO_OBJ_FIELD(obj, index) ((obj)->fields[index])

#define PICO_OBJECT_SET_FIELD(obj, field_index, value)                         \
    (obj)->fields[(field_index)] = (value);

#define PICO_MAX_FRAMES 512
#define PICO_MAX_STACK_SIZE 2048
#define PICO_FRAME_NEW(func, stk, parent_frame)                                \
    (pico_frame) {                                                             \
        .function = (func), .stack = (stk), .ip = 0,                           \
        .locals = calloc((func)->local_count, sizeof(pico_value)),             \
        .parent = parent_frame                                                 \
    }

#define PICO_FRAME_DEINIT(frame)                                               \
    do {                                                                       \
        free((frame).locals);                                                  \
        (frame).locals = NULL;                                                 \
    } while (0)

#define PICO_EXPORT __attribute__((visibility("default")))

typedef int32_t pint;
typedef uint8_t pbyte;
typedef uint32_t puint;
typedef int16_t pshort;
typedef char pchar;
typedef char *pstr;
typedef uint64_t pulong;
typedef bool pbool;

typedef struct pico_env pico_env;

typedef enum pico_value_kind {
    PICO_INT,
    PICO_BOOL,
    PICO_STRING,
    PICO_OBJECT,
} pico_value_kind_t;

typedef struct pico_value {
    pico_value_kind_t kind;
    union {
        pint i_value;
        struct {
            puint size;
            pstr s_value;
        };
        struct pico_object *objref;
        pbool boolean;
    };
} pico_value;

typedef struct pico_object {
    pbyte num_fields;
    pbyte is_forwarded;
    pico_value fields[];
} pico_object;

static pico_value pico_true = (pico_value){.kind = PICO_BOOL, .boolean = true};
static pico_value pico_false =
    (pico_value){.kind = PICO_BOOL, .boolean = false};

typedef struct pico_function {
    puint name_id;
    pbyte *code;
    puint local_count;
    puint param_count;
    pulong code_len;
} pico_function;

typedef struct bytecode_unit {
    pico_value *constants;
    pico_function *functions;
    puint main_function_index;
} bytecode_unit;

typedef struct pico_frame {
    pico_function *function;
    pico_value *stack;
    pico_value *locals;
    pulong ip;
    struct pico_frame *parent;
} pico_frame;

typedef struct pico_vm {
    pulong fc;
    pulong sp;
    pico_frame frames[PICO_MAX_FRAMES];
    pico_value stack[PICO_MAX_STACK_SIZE];
    pico_value *constants;
    pico_function *functions;
    puint main_function_index;
} pico_vm;

struct pico_env {
    pico_vm *vm;
    pico_frame *frame;
    pico_gc *gc;
    struct native_fn_entry *native_functions;
    void **lib_handles;
};

typedef pico_value (*pico_native_fn)(pico_env *env, pico_value *args);
typedef void (*pico_lib_init)(pico_env *env);

typedef struct native_fn_entry {
    const char *name;
    pico_native_fn handle;
    UT_hash_handle hh;
} native_fn_entry;

bytecode_unit load_bytecode(const char *filename);
void print_bytecode_unit(bytecode_unit *unit);

void pico_env_init(pico_env *env);
void pico_env_deinit(pico_env *env);

void pico_vm_init(pico_vm *vm, bytecode_unit *unit);
void pico_vm_run(pico_env *env);
void pico_vm_shutdown(pico_vm *vm);

void pico_load_libraries(pico_env *env, const char *lib_name);
void pico_deinit_libraries(void **lib_handles);

/**
 * Move these functions to a separate source file.
 */
/**--------------------------------------------- */
static inline void pico_register_native_function(pico_env *env,
                                                 const char *name,
                                                 pico_native_fn handle) {

    native_fn_entry *entry = malloc(sizeof(*entry));
    entry->handle = handle;
    entry->name = strdup(name);
    HASH_ADD_KEYPTR(hh, env->native_functions, entry->name, strlen(entry->name),
                    entry);
}

static inline pico_object *pico_env_alloc_object(pico_env *env,
                                                 puint num_fields) {

    pico_object *obj = (pico_object *)pico_gc_alloc(env->gc, num_fields);
    if (!obj) {
        pico_gc_collect(env->gc, env);
        flip_spaces(env->gc);
        obj = (pico_object *)pico_gc_alloc(env->gc, num_fields);
        if (!obj) {
            if (!pico_gc_extend_spaces(env->gc, env)) {
                fprintf(
                    stderr,
                    "PicoGC: failed to allocate object (%u fields) even after "
                    "GC and heap extension (heap=%zu bytes).\n",
                    num_fields, env->gc->heap_size);
                pico_env_deinit(env);
                exit(EXIT_FAILURE);
            }
            obj = (pico_object *)pico_gc_alloc(env->gc, num_fields);
            if (!obj) {
                fprintf(
                    stderr,
                    "PicoGC: failed to allocate object (%u fields) even after "
                    "GC and heap extension (heap=%zu bytes).\n",
                    num_fields, env->gc->heap_size);
                pico_env_deinit(env);
                exit(EXIT_FAILURE);
            }
        }
    }
    return obj;
}
/**--------------------------------------------- */
