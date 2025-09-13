#pragma once

#include "gc.h"
#include "uthash.h"
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define DECLARE_LIB_FN(prefix, name)                                           \
    PICO_EXPORT pico_value prefix##name(pico_env *env, pico_value *args)

#define PICO_LIB_FN(prefix, name)                                              \
    PICO_EXPORT pico_value prefix##name(pico_env *env, pico_value *args)

#define PICO_LIB_FN_VOID(prefix, name)                                         \
    PICO_EXPORT void prefix##name(pico_env *env, pico_value *args)

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

#define PICO_GET_OBJECT_FIELD_PTR(obj, index) (&((obj)->fields[(index)]))
#define PICO_GET_OBJECT_FIELD(obj, index) ((obj)->fields[(index)])

#define PICO_OBJECT_GET_INT_FIELD(obj, index) ((obj)->fields[(index)].i_value)
#define PICO_OBJECT_GET_BOOL_FIELD(obj, index) ((obj)->fields[(index)].boolean)
#define PICO_OBJECT_GET_STR_FIELD(obj, index) ((obj)->fields[(index)].s_value)
#define PICO_OBJECT_GET_STR_LEN(obj, index) ((obj)->fields[(index)].size)
#define PICO_OBJECT_GET_OBJ_FIELD(obj, index) ((obj)->fields[(index)].objref)

#define PICO_POP_INT(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].i_value)
#define PICO_POP_STR(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].s_value)
#define PICO_POP_OBJ(vm_ptr) ((vm_ptr)->stack[--((vm_ptr)->sp)].objref)


#define GET_ARG_INT(args, idx)     ((args)[(idx)].i_value)
#define GET_ARG_BOOL(args, idx)    ((args)[(idx)].boolean)
#define GET_ARG_STR(args, idx)     ((args)[(idx)].s_value)
#define GET_ARG_STR_LEN(args, idx) ((args)[(idx)].size)
#define GET_ARG_OBJ(args, idx)     ((args)[(idx)].objref)
#define GET_ARG_VAL(args, idx)     ((args)[(idx)])


#define PICO_OBJ_FIELD_PTR(obj, index) (&((obj)->fields[index]))
#define PICO_OBJ_FIELD(obj, index) ((obj)->fields[index])

#define PICO_OBJECT_SET_FIELD(obj, field_index, value)                         \
    (obj)->fields[(field_index)] = (value);

#define PICO_MAX_FRAMES 512
#define PICO_MAX_STACK_SIZE 2048
#define PICO_FRAME_NEW(func, base, stack_ptr, parent_frame)                    \
    (pico_frame) {                                                             \
        .function = (func), .bp = (base), .sp = (stack_ptr), .ip = 0,          \
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
    pico_value fields[];
} pico_object;

static pico_value pico_true = (pico_value){.kind = PICO_BOOL, .boolean = true};
static pico_value pico_false =
    (pico_value){.kind = PICO_BOOL, .boolean = false};

static pico_value pico_one = (pico_value){.kind = PICO_INT, .i_value = 1};
static pico_value pico_zero = (pico_value){.kind = PICO_INT, .i_value = 0};

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
    pico_value *bp;
    pico_value *sp;
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
typedef void (*pico_native_void_fn)(pico_env *env, pico_value *args);

typedef void (*pico_lib_init)(pico_env *env);

typedef enum { NATIVE_RETURNS_VALUE, NATIVE_RETURNS_VOID } native_fn_kind;

typedef struct native_fn_entry {
    const char *name;
    native_fn_kind kind;
    puint param_count;
    union {
        pico_native_fn value_handle;
        pico_native_void_fn void_handle;
    };
    UT_hash_handle hh;
} native_fn_entry;

bytecode_unit load_bytecode(const char *filename);
void print_bytecode_unit(bytecode_unit *unit);

void pico_env_init(pico_env *env);
void pico_env_deinit(pico_env *env);

void pico_vm_init(pico_vm *vm, bytecode_unit *unit);
void pico_vm_run(pico_env *env);
void pico_vm_shutdown(pico_vm *vm);

void pico_load_libraries(pico_env *env, char *lib_name);
void pico_deinit_libraries(void **lib_handles);

/**
 * Move these functions to a separate source file.
 */
/**--------------------------------------------- */
static inline void pico_register_native_function(pico_env *env,
                                                 const char *name,
                                                 puint param_count,
                                                 pico_native_fn handle) {

    native_fn_entry *entry = malloc(sizeof(*entry));
    entry->name = strdup(name);
    entry->kind = NATIVE_RETURNS_VALUE;
    entry->param_count = param_count;
    entry->value_handle = handle;
    HASH_ADD_KEYPTR(hh, env->native_functions, entry->name, strlen(entry->name),
                    entry);
}

static inline void
pico_register_native_void_function(pico_env *env, const char *name,
                                   puint param_count,
                                   pico_native_void_fn handle) {

    native_fn_entry *entry = malloc(sizeof(*entry));
    entry->name = strdup(name);
    entry->kind = NATIVE_RETURNS_VOID;
    entry->param_count = param_count;
    entry->void_handle = handle;
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
