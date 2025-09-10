#include "worklist.h"
#include "pico.h"
#include <stdlib.h>

void object_worklist_enqueue(object_worklist *worklist, pico_value *object) {
    object_worklist_item *item = malloc(sizeof(object_worklist_item));
    if (!worklist->head) {
        worklist->head = worklist->tail = item;
        return;
    }
    item->object = object;
    item->next = nullptr;
    worklist->tail->next = item;
    worklist->tail = item;
}

pico_value *object_worklist_dequeue(object_worklist *worklist) {
    object_worklist_item *item = worklist->head;
    if (!item)
        return nullptr;
    pico_value *object = item->object;
    worklist->head = item->next;
    free(item);
    return object;
}
