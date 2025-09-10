#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct pico_env pico_env;

typedef struct gc_semi_space {
    size_t size;
    uint8_t *space_start;
    uint8_t *alloc_ptr;
    uint8_t *space_end;
} gc_semi_space;

typedef struct pico_gc {
    gc_semi_space from_space;
    gc_semi_space to_space;
    size_t total_objects;
    size_t heap_size;
} pico_gc;

gc_semi_space gc_semi_space_new(size_t size);
pico_gc *pico_gc_new(size_t heap_size);
bool pico_gc_extend_spaces(pico_gc *gc, pico_env *env);
void pico_gc_destroy(pico_gc *gc);
uint8_t *pico_gc_alloc(pico_gc *gc, uint32_t num_fields);
void pico_gc_collect(pico_gc *gc, pico_env *env);
void flip_spaces(pico_gc *gc);
