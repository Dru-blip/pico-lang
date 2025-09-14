#include "opcodes.h"
#include "pico.h"
#include "stb_ds.h"
#include "uthash.h"

#include <stdlib.h>

#ifdef DEBUG_BUILD
#include "debugger.h"
#endif

#define READ_OPCODE() frame->function->code[frame->ip++]
#define READ_TWO_BYTES() (READ_OPCODE() | (READ_OPCODE() << 8))
#define READ_CONSTANT(vm) (vm->constants[READ_TWO_BYTES()])

#define PUSH(val) (*((frame)->sp)++ = (val))
#define POP() (*--((frame)->sp))
#define PEEK(frame) (frame->sp - 1)

#define BINARY_ARITH_INT(frame, op)                                            \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(TO_PICO_INT(a.i_value op b.i_value));

#define COMPARE_INT(frame, op)                                                 \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(((a.i_value op b.i_value) ? PICO_TRUE : PICO_FALSE));

#define LOGICAL_OP(frame, op)                                                  \
    const pico_value b = POP();                                                \
    const pico_value a = POP();                                                \
    PUSH(((a.boolean op b.boolean) ? PICO_TRUE : PICO_FALSE));

static void pico_run_frame(pico_env *env, pico_vm *vm, pico_frame *frame) {
frame_start:
    pulong code_len = frame->function->code_len;
    while (frame->ip < code_len) {

#ifdef DEBUG_BUILD
        dbg_event *event = dbg_event_queue_pop(env->event_queue);
        if (event) {
            switch (event->kind) {
            case DBG_EVENT_PAUSE: {
                vm->state = PICO_VM_STATE_PAUSED;
                break;
            }
            }
        }

        if (vm->state == PICO_VM_STATE_PAUSED) {
            continue;
        }
#endif

        const pbyte opcode = READ_OPCODE();
        switch (opcode) {
        case OP_LIC: {
            PUSH(READ_CONSTANT(vm));
            break;
        }
        case OP_LSC: {
            PUSH(READ_CONSTANT(vm));
            break;
        }
        case OP_STORE: {
            puint index = READ_TWO_BYTES();
            frame->locals[index] = POP();
            break;
        }
        case OP_LOAD: {
            puint index = READ_TWO_BYTES();
            PUSH(frame->locals[index]);
            break;
        }
        case OP_IINC: {
            puint index = READ_TWO_BYTES();
            frame->locals[index].i_value++;
            break;
        }
        case OP_IDEC: {
            puint index = READ_TWO_BYTES();
            frame->locals[index].i_value--;
            break;
        }
        case OP_IADD: {
            BINARY_ARITH_INT(frame, +)
            break;
        }
        case OP_ISUB: {
            BINARY_ARITH_INT(frame, -)
            break;
        }
        case OP_IMUL: {
            BINARY_ARITH_INT(frame, *)
            break;
        }
        case OP_IDIV: {
            BINARY_ARITH_INT(frame, /)
            break;
        }
        case OP_IREM: {
            BINARY_ARITH_INT(frame, %)
            break;
        }
        case OP_IBAND: {
            BINARY_ARITH_INT(frame, &)
            break;
        }
        case OP_IBOR: {
            BINARY_ARITH_INT(frame, |)
            break;
        }
        case OP_IBXOR: {
            BINARY_ARITH_INT(frame, ^)
            break;
        }
        case OP_ISHL: {
            BINARY_ARITH_INT(frame, <<)
            break;
        }
        case OP_ISHR: {
            BINARY_ARITH_INT(frame, >>)
            break;
        }

        case OP_IEQ: {
            COMPARE_INT(frame, ==)
            break;
        }
        case OP_INE: {
            COMPARE_INT(frame, !=)
            break;
        }
        case OP_ILT: {
            COMPARE_INT(frame, <)
            break;
        }
        case OP_ILE: {
            COMPARE_INT(frame, <=)
            break;
        }
        case OP_IGT: {
            COMPARE_INT(frame, >)
            break;
        }
        case OP_IGE: {
            COMPARE_INT(frame, >=)
            break;
        }

        case OP_IAND: {
            LOGICAL_OP(frame, &&)
            break;
        }
        case OP_IOR: {
            LOGICAL_OP(frame, ||) break;
        }
        case OP_LBT: {
            PUSH(pico_true);
            break;
        }
        case OP_LBF: {
            PUSH(pico_false);
            break;
        }
        case OP_I2B: {
            const pico_value a = POP();
            PUSH(a.i_value ? pico_true : pico_false);
            break;
        }
        case OP_L2B: {
            // TODO: implement long to boolean
            break;
        }
        case OP_B2L: {
            const pico_value a = POP();
            PUSH(a.boolean ? pico_one : pico_zero);
            break;
        }
        case OP_B2I: {
            const pico_value a = POP();
            PUSH(a.boolean ? pico_one : pico_zero);
            break;
        }
        case OP_I2L: {
            // TODO: implement int to long
            break;
        }
        case OP_L2I: {
            // TODO: implement long to int
            break;
        }
        case OP_BNOT: {
            const pico_value a = POP();
            PUSH(a.boolean ? pico_false : pico_true);
            break;
        }
        case OP_LOG: {
            const pico_value a = POP();
            printf("%d\n", a.i_value);
            break;
        }
        case OP_JF: {
            const pico_value a = POP();
            if (!a.boolean) {
                puint jmp_index = READ_TWO_BYTES();
                frame->ip = jmp_index;
            }
            break;
        }
        case OP_JMP: {
            puint jmp_index = READ_TWO_BYTES();
            frame->ip = jmp_index;
            break;
        }
        case OP_CALL: {
            puint function_index = READ_TWO_BYTES();
            pico_function *function = &vm->functions[function_index];
            pico_frame child_frame =
                PICO_FRAME_NEW(function, frame->sp, frame->sp, frame);
            vm->frames[vm->fc++] = child_frame;
            frame = &vm->frames[vm->fc - 1];
            env->frame = frame;
            for (pint i = function->param_count - 1; i >= 0; i--) {
                frame->locals[i] = POP();
            }
            goto frame_start;
        }
        case OP_VOID_CALL_EXTERN: {
            puint name_index = READ_TWO_BYTES();
            pico_value *fn_name = &vm->constants[name_index];
            native_fn_entry *entry;
            HASH_FIND_STR(env->native_functions, fn_name->s_value, entry);
            if (!entry) {
                printf("cannot find function: %s\n", fn_name->s_value);
                exit(EXIT_FAILURE);
            }
            pico_value *args = frame->sp - entry->param_count;
            entry->void_handle(env, args);
            frame->sp -= entry->param_count;
            break;
        }
        case OP_CALL_EXTERN: {
            puint name_index = READ_TWO_BYTES();
            pico_value *fn_name = &vm->constants[name_index];
            native_fn_entry *entry;
            HASH_FIND_STR(env->native_functions, fn_name->s_value, entry);
            if (!entry) {
                printf("cannot find function: %s\n", fn_name->s_value);
                exit(EXIT_FAILURE);
            }
            pico_value *args = frame->sp - entry->param_count;
            frame->sp -= entry->param_count;
            PUSH(entry->value_handle(env, args));
            break;
        }
        case OP_RET: {
            if (frame->parent) {
                pico_frame *child_frame = frame;
                frame = frame->parent;
                --vm->fc;
                env->frame = frame;
                PICO_FRAME_DEINIT(*child_frame);
                vm->sp = frame->sp - vm->stack;
                goto frame_start;
            }
            vm->sp = frame->sp - vm->stack;
            env->frame = nullptr;
            goto frame_end;
        }
        case OP_ALLOCA_STRUCT: {
            puint num_fields = READ_TWO_BYTES();
            pico_object *obj = pico_env_alloc_object(env, num_fields);
            PUSH(TO_PICO_OBJ(obj));
            break;
        }
        case OP_SET_FIELD: {
            puint field_index = READ_TWO_BYTES();
            pico_value value = POP();
            pico_value *obj = PEEK(frame);
            PICO_OBJECT_SET_FIELD(obj->objref, field_index, value);
            break;
        }
        case OP_STORE_FIELD: {
            puint field_index = READ_TWO_BYTES();
            pico_value obj = POP();
            PICO_OBJECT_SET_FIELD(obj.objref, field_index, *PEEK(frame));
            break;
        }
        case OP_LOAD_FIELD: {
            puint field_index = READ_TWO_BYTES();
            pico_value obj = POP();
            PUSH(PICO_OBJ_FIELD(obj.objref, field_index));
            break;
        }
        case OP_IFIELD_INC: {
            puint field_index = READ_TWO_BYTES();
            pico_object *obj = POP().objref;
            (&obj->fields[field_index])->i_value++;
            break;
        }
        case OP_IFIELD_DEC: {
            puint field_index = READ_TWO_BYTES();
            pico_object *obj = POP().objref;
            (&obj->fields[field_index])->i_value--;
            break;
        }
        }
    }

frame_end:;
}

void pico_vm_init(pico_vm *vm, bytecode_unit *unit) {
    vm->main_function_index = unit->main_function_index;
    vm->constants = unit->constants;
    vm->fc = 0;
    vm->functions = unit->functions;
    vm->sp = 0;
}

void pico_vm_run(pico_env *env) {
    // get the main function
    pico_function *main_func =
        &env->vm->functions[env->vm->main_function_index];

    // push the main function onto the call stack
    pico_frame frame = PICO_FRAME_NEW(main_func, &env->vm->stack[env->vm->sp],
                                      &env->vm->stack[env->vm->sp], nullptr);
    env->vm->frames[env->vm->fc++] = frame;
    pico_run_frame(env, env->vm, &frame);
    PICO_FRAME_DEINIT(frame);
}

void pico_vm_shutdown(pico_vm *vm) {
    pulong len = arrlen(vm->constants);
    for (puint i = 0; i < len; i++) {
        const pico_value *value = &vm->constants[i];
        if (value->kind == PICO_STRING) {
            free(value->s_value);
        }
    }

    len = arrlen(vm->functions);
    for (puint i = 0; i < len; i++) {
        free(vm->functions[i].code);
    }
}
