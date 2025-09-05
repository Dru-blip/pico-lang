#pragma once

#include "ast.h"
#include <stddef.h>
#include <stdint.h>

typedef uint32_t node_index_t;

typedef struct node_iter {
    void *nodes;
    node_index_t current;
    node_index_t (*get_next)(void *nodes, node_index_t idx);
} NodeIter;


inline NodeIter node_iter_init(
    void *nodes,
    node_index_t start,
    node_index_t (*get_next)(void *, node_index_t)
) {
    NodeIter it;
    it.nodes = nodes;
    it.current = start;
    it.get_next = get_next;
    return it;
}


inline void* node_iter_next(NodeIter *it) {
    if (it->current == UINT32_MAX) return nullptr;
    void *node = (char*)it->nodes + it->current;
    it->current = it->get_next(it->nodes, it->current);
    return node;
}
