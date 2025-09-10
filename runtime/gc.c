#include "gc.h"
#include "pico.h"
#include "worklist.h"
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define IS_OBJECT_IN_TOSPACE(obj) ((uint8_t *)obj >= gc->to_space.space_start)

void flip_spaces(pico_gc *gc) {
    gc_semi_space temp = gc->from_space;
    gc->from_space = gc->to_space;
    gc->to_space = temp;
}

gc_semi_space gc_semi_space_new(size_t size) {
    gc_semi_space space;
    space.size = size;
    space.space_start = malloc(size);
    space.space_end = space.space_start + size;
    space.alloc_ptr = space.space_start;
    return space;
}

pico_gc *pico_gc_new(size_t heap_size) {
    pico_gc *gc = malloc(sizeof(pico_gc));
    gc->from_space = gc_semi_space_new(heap_size);
    gc->to_space = gc_semi_space_new(heap_size);
    gc->total_objects = 0;
    gc->heap_size = heap_size;
    return gc;
}

static void gc_semi_space_destroy(gc_semi_space *space) {
    free(space->space_start);
    space->space_start = NULL;
    space->space_end = NULL;
    space->alloc_ptr = NULL;
    space->size = 0;
}

bool pico_gc_extend_spaces(pico_gc *gc, pico_env *env) {
    size_t new_size = gc->heap_size * 2;
    gc_semi_space new_from_space = gc_semi_space_new(new_size);
    gc_semi_space new_to_space = gc_semi_space_new(new_size);

    if (!new_from_space.space_start || !new_to_space.space_start) {
        return false;
    }

    gc_semi_space old_to_space = gc->to_space;
    gc_semi_space old_from_space = gc->from_space;

    gc->to_space = new_from_space;
    pico_gc_collect(gc, env);
    gc->from_space = new_to_space;
    flip_spaces(gc);
    gc_semi_space_destroy(&old_to_space);
    gc_semi_space_destroy(&old_from_space);
    gc->heap_size = new_size;
    return true;
}

void pico_gc_destroy(pico_gc *gc) {
    gc_semi_space_destroy(&gc->from_space);
    gc_semi_space_destroy(&gc->to_space);
    free(gc);
}

uint8_t *pico_gc_alloc(pico_gc *gc, uint32_t num_fields) {
    size_t size = sizeof(pico_object) + num_fields * sizeof(pico_value);
    if (gc->from_space.alloc_ptr + size > gc->from_space.space_end) {
        return nullptr;
    }
    pico_object *obj = (pico_object *)gc->from_space.alloc_ptr;
    obj->num_fields = num_fields;
    gc->from_space.alloc_ptr += size;
    return (uint8_t *)obj;
}

static pico_object *gc_copy_object(pico_gc *gc, pico_object *obj) {
    if (IS_OBJECT_IN_TOSPACE(obj)) {
        return obj;
    }
    size_t size = sizeof(pico_object) + obj->num_fields * sizeof(pico_value);
    pico_object *new_obj = (pico_object *)gc->to_space.alloc_ptr;
    memcpy(new_obj, obj, size);
    gc->to_space.alloc_ptr += size;
    new_obj->is_forwarded = true;
    return new_obj;
}

void pico_gc_copy_root(pico_gc *gc, pico_value *obj) {
    object_worklist worklist;
    worklist.head = worklist.tail = nullptr;
    object_worklist_enqueue(&worklist, obj);
    while (worklist.head) {
        pico_value *current = object_worklist_dequeue(&worklist);
        current->objref = gc_copy_object(gc, current->objref);
        for (puint i = 0; i < current->objref->num_fields; i++) {
            if (current->objref->fields[i].kind == PICO_OBJECT) {
                object_worklist_enqueue(&worklist, &current->objref->fields[i]);
            }
        }
    }
}

void pico_gc_collect(pico_gc *gc, pico_env *env) {
    for (puint i = 0; i < PICO_MAX_STACK_SIZE; i++) {
        pico_value *value = &env->vm->stack[i];
        if (value->kind == PICO_OBJECT) {
            pico_gc_copy_root(gc, value);
        }
    }
}
