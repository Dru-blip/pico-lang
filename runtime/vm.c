#include "vm.h"
#include "frame.h"
#include "opcodes.h"
#include "pico.h"
#include "stb_ds.h"
#include <stdio.h>
#include <stdlib.h>

#define READ_OPCODE() frame->function->code[frame->ip++]
#define READ_TWO_BYTES() (READ_OPCODE() | (READ_OPCODE() << 8))
#define READ_CONSTANT() vm.constants[READ_TWO_BYTES()]

#define PUSH(value) vm.stack[vm.sp++] = value;
#define POP() vm.stack[--vm.sp]

#define BINARY_INT_OP(op)                                                      \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(TO_PICO_INT(a.i_value op b.i_value));

static pico_vm vm;

static void pico_run_frame(pico_frame *frame) {
    const pulong code_len = frame->function->code_len;
    while (frame->ip < code_len) {
        const pbyte opcode = READ_OPCODE();
        switch (opcode) {
        case OP_LIC: {
            PUSH(READ_CONSTANT())
            break;
        }
        case OP_IADD: {
            BINARY_INT_OP(+)
            break;
        }
        case OP_ISUB: {
            BINARY_INT_OP(-)
            break;
        }
        case OP_IMUL: {
            BINARY_INT_OP(*)
            break;
        }
        case OP_IDIV: {
            BINARY_INT_OP(/)
            break;
        }
        case OP_IREM: {
            BINARY_INT_OP(%)
            break;
        }
        case OP_LOG: {
            const pico_value a=POP();
            printf("%d\n", a.i_value);
            break;
        }
        case OP_RET: {
            return;
        }
        }
    }
}

void pico_vm_init(bytecode_unit *unit) {
    vm.constants = unit->constants;
    vm.fc = 0;
    vm.functions = unit->functions;
    vm.sp = 0;
}

void pico_vm_run() {
    // get the main function
    pico_function *main_func = &vm.functions[0];

    // push the main function onto the call stack
    pico_frame frame = PICO_FRAME_NEW(main_func, &vm.stack[vm.sp]);
    vm.frames[vm.fc++] = frame;
    pico_run_frame(&frame);
}

void pico_vm_shutdown() {
    pulong len = arrlen(vm.constants);
    for (puint i = 0; i < len; i++) {
        const pico_value *value = &vm.constants[i];
        if (value->kind == PICO_STRING) {
            free(value->s_value);
        }
    }

    len = arrlen(vm.functions);
    for (puint i = 0; i < len; i++) {
        free(vm.functions[i].code);
    }
}
