#include "opcodes.h"
#include "pico.h"
#include "stb_ds.h"
#include <stdio.h>

typedef struct {
    pbyte opcode;
    const char *name;
    int operands;
    void (*print_fp)(pbyte *, pulong *);
} opcode_info;

static pico_value *constants;

void print_operand_two(pbyte *code, pulong *pc) {
    printf("%d", code[*pc + 1] | (code[*pc + 2] << 8));
}

void print_constant_operand(pbyte *code, pulong *pc) {
    puint index = code[*pc + 1] | (code[*pc + 2] << 8);
    pico_value *value = &constants[index];
    switch (value->kind) {
    case PICO_INT: {
        printf("$%d", value->i_value);
        break;
    }
    case PICO_STRING: {
        printf("'%s'", value->s_value);
        break;
    }
    default: {
        printf("unknown");
        break;
    }
    }
}

static const opcode_info opcode_table[] = {
    {OP_LIC, "LoadConstInt", 2, print_constant_operand},
    {OP_LSC, "LoadConstString", 2, print_constant_operand},
    {OP_LBT, "LoadBoolTrue", 0, NULL},
    {OP_LBF, "LoadBoolFalse", 0, NULL},
    {OP_ISTORE, "IStore", 2, print_operand_two},
    {OP_ILOAD, "Iload", 2, print_operand_two},

    {OP_IADD, "IAdd", 0, NULL},
    {OP_ISUB, "ISub", 0, NULL},
    {OP_IMUL, "IMul", 0, NULL},
    {OP_IDIV, "IDiv", 0, NULL},
    {OP_IREM, "IRem", 0, NULL},
    {OP_IAND, "IAnd", 0, NULL},
    {OP_IOR, "IOr", 0, NULL},
    {OP_IBAND, "IBand", 0, NULL},
    {OP_IBOR, "IBor", 0, NULL},
    {OP_IBXOR, "IBxor", 0, NULL},
    {OP_ISHL, "IShl", 0, NULL},
    {OP_ISHR, "IShr", 0, NULL},

    {OP_IEQ, "IEq", 0, NULL},
    {OP_INE, "INe", 0, NULL},
    {OP_ILT, "ILt", 0, NULL},
    {OP_ILE, "ILe", 0, NULL},
    {OP_IGT, "IGt", 0, NULL},
    {OP_IGE, "IGe", 0, NULL},

    {OP_L2B, "LongToBool", 0, NULL},
    {OP_L2I, "LongToInt", 0, NULL},
    {OP_I2L, "IntToLong", 0, NULL},
    {OP_I2B, "IntToBool", 0, NULL},

    {OP_JF, "Jf", 2, print_operand_two},
    {OP_JMP, "Jmp", 2, print_operand_two},
    {OP_RET, "Ret", 0, NULL},
    {OP_CALL, "Call", 2, print_operand_two},
    {OP_VOID_CALL, "VoidCall", 2, print_operand_two},
    {OP_VOID_CALL_EXTERN, "VoidCallExtern", 2, print_operand_two},
    {OP_CALL_EXTERN, "CallExtern", 2, print_operand_two},

    {OP_ALLOCA_STRUCT, "AllocaStruct", 2, print_operand_two},
    {OP_SET_FIELD, "SetField", 2, print_operand_two},

    {OP_LOG, "Log", 0, NULL},

    {0xFF, "unknown", 0, NULL} // sentinel
};

static const opcode_info *get_info(pbyte op) {
    for (int i = 0; opcode_table[i].opcode != 0xFF; i++) {
        if (opcode_table[i].opcode == op)
            return &opcode_table[i];
    }
    return &opcode_table[sizeof(opcode_table) / sizeof(opcode_table[0]) - 1];
}

static void print_function(const pico_function *fn, int index) {
    printf("Function %d (name_id=%u, locals=%u, code_len=%lu):\n", index,
           fn->name_id, fn->local_count, fn->code_len);

    int index_width = snprintf(NULL, 0, "%lu", fn->code_len);

    pulong pc = 0;
    while (pc < fn->code_len) {
        pbyte op = fn->code[pc];
        const opcode_info *info = get_info(op);
        puint size = 1 + info->operands;

        printf("%*lu |> ", index_width, pc);
        for (puint i = 0; i < size && pc + i < fn->code_len; i++) {
            printf("%02X ", fn->code[pc + i]);
        }
        for (puint i = size; i < 4; i++)
            printf("   ");

        printf("%-12s", info->name);

        if (info->print_fp) {
            printf("%-15s", "");
            info->print_fp(fn->code, &pc);
        }

        printf("\n");
        pc += size;
    }
    printf("\n");
}

void print_bytecode_unit(bytecode_unit *unit) {
    const puint num_functions = arrlen(unit->functions);
    constants = unit->constants;
    for (puint i = 0; i < num_functions; i++) {
        print_function(&unit->functions[i], i);
    }
}
