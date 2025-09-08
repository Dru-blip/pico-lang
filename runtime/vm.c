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

#define BINARY_ARITH_INT(op)                                                   \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(TO_PICO_INT(a.i_value op b.i_value));

#define COMPARE_INT(op)                                                        \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(((a.i_value op b.i_value) ? PICO_TRUE : PICO_FALSE));

#define LOGICAL_OP(op)                                                         \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(((a.boolean op b.boolean) ? PICO_TRUE : PICO_FALSE));

static pico_vm vm;

static void pico_run_frame(pico_frame *frame) {
frame_start:
    pulong code_len = frame->function->code_len;
    while (frame->ip < code_len) {
        const pbyte opcode = READ_OPCODE();
        switch (opcode) {
        case OP_LIC: {
            PUSH(READ_CONSTANT())
            break;
        }
        case OP_ISTORE: {
            puint index = READ_TWO_BYTES();
            frame->locals[index] = POP();
            break;
        }
        case OP_ILOAD: {
            puint index = READ_TWO_BYTES();
            PUSH(frame->locals[index]);
            break;
        }
        case OP_IADD: {
            BINARY_ARITH_INT(+)
            break;
        }
        case OP_ISUB: {
            BINARY_ARITH_INT(-)
            break;
        }
        case OP_IMUL: {
            BINARY_ARITH_INT(*)
            break;
        }
        case OP_IDIV: {
            BINARY_ARITH_INT(/)
            break;
        }
        case OP_IREM: {
            BINARY_ARITH_INT(%)
            break;
        }
        case OP_IBAND: {
            BINARY_ARITH_INT(&)
            break;
        }
        case OP_IBOR: {
            BINARY_ARITH_INT(|)
            break;
        }
        case OP_IBXOR: {
            BINARY_ARITH_INT(^)
            break;
        }
        case OP_ISHL: {
            BINARY_ARITH_INT(<<)
            break;
        }
        case OP_ISHR: {
            BINARY_ARITH_INT(>>)
            break;
        }
        case OP_IEQ: {
            COMPARE_INT(==)
            break;
        }
        case OP_INE: {
            COMPARE_INT(!=)
            break;
        }
        case OP_ILT: {
            COMPARE_INT(<)
            break;
        }
        case OP_ILE: {
            COMPARE_INT(<=)
            break;
        }
        case OP_IGT: {
            COMPARE_INT(>)
            break;
        }
        case OP_IGE: {
            COMPARE_INT(>=)
            break;
        }
        case OP_IAND: {
            LOGICAL_OP(&&)
            break;
        }
        case OP_IOR: {
            LOGICAL_OP(||)
            break;
        }
        case OP_LOG: {
            const pico_value a = POP();
            printf("%d\n", a.i_value);
            break;
        }
        case OP_JF: {
            const pico_value a = POP();
            if (!a.i_value) {
                puint offset = READ_TWO_BYTES();
                frame->ip = offset;
            }
            break;
        }
        case OP_JMP: {
            puint offset = READ_TWO_BYTES();
            frame->ip = offset;
            break;
        }
        case OP_CALL: {
            puint function_index = READ_TWO_BYTES();
            pico_function *function = &vm.functions[function_index];
            pico_frame child_frame =
                PICO_FRAME_NEW(function, &vm.stack[vm.sp], frame);
            vm.frames[vm.fc++] = child_frame;
            frame = &child_frame;
            for (pint i = function->param_count - 1; i >= 0; i--) {
                frame->locals[i] = POP();
            }
            goto frame_start;
        }
        case OP_RET: {
            if (frame->parent) {
                pico_frame *child_frame = frame;
                frame = frame->parent;
                --vm.fc;
                PICO_FRAME_DEINIT(*child_frame);
                goto frame_start;
            }
            goto end;
        }
        }
    }

end:;
}

void pico_vm_init(bytecode_unit *unit) {
    vm.main_function_index = unit->main_function_index;
    vm.constants = unit->constants;
    vm.fc = 0;
    vm.functions = unit->functions;
    vm.sp = 0;
}

void pico_vm_run() {
    // get the main function
    pico_function *main_func = &vm.functions[vm.main_function_index];

    // push the main function onto the call stack
    pico_frame frame = PICO_FRAME_NEW(main_func, &vm.stack[vm.sp], nullptr);
    vm.frames[vm.fc++] = frame;
    pico_run_frame(&frame);
    PICO_FRAME_DEINIT(frame);
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
