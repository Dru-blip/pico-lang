#pragma once

#include "pico.h"

typedef struct object_worklist_item {
    pico_value *object;
    struct object_worklist_item *next;
} object_worklist_item;

typedef struct object_worklist {
    object_worklist_item *head;
    object_worklist_item *tail;
} object_worklist;

void object_worklist_enqueue(object_worklist *worklist, pico_value *object);
pico_value *object_worklist_dequeue(object_worklist *worklist);
