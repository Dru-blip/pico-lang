#pragma once

#include "frame.h"
#include "function.h"
#include "loader.h"
#include "pico.h"

#define PICO_MAX_FRAMES 512
#define PICO_MAX_STACK 2048

typedef struct pico_vm {
    pulong fc;
    pulong sp;
    pico_frame frames[PICO_MAX_FRAMES];
    pico_value stack[PICO_MAX_STACK];
    pico_value *constants;
    pico_function *functions;
    puint main_function_index;
} pico_vm;

void pico_vm_init(bytecode_unit *unit);
void pico_vm_run();
void pico_vm_shutdown();
