from hir import FunctionBlock, HirBlock, HirNodeTag
from pico_ast import OpTag
from pico_types import TypeRegistry
from symtab import Linkage

# data
OP_LIC = 0x05
OP_LSC = 0x06
OP_LBT = 0x07
OP_LBF = 0x08
OP_STORE = 0x09
OP_ISTORE = 0x0A
OP_ILOAD = 0x0B
OP_LOAD = 0x0C
OP_IINC = 0x0D
OP_IDEC = 0x0E

# integer arithmetic
OP_IADD = 0x20
OP_ISUB = 0x21
OP_IMUL = 0x22
OP_IDIV = 0x23
OP_IREM = 0x24
OP_IAND = 0x25
OP_IOR = 0x26
OP_IBAND = 0x27
OP_IBOR = 0x28
OP_IBXOR = 0x29
OP_ISHL = 0x2A
OP_ISHR = 0x2B

OP_IEQ = 0x2C
OP_INE = 0x2D
OP_ILT = 0x2E
OP_ILE = 0x2F
OP_IGT = 0x30
OP_IGE = 0x31

OP_BNOT = 0x55
# casting
OP_B2I = 0x59
OP_B2L = 0x5A
OP_L2B = 0x5B
OP_L2I = 0x5C
OP_I2L = 0x5D
OP_I2B = 0x5E

# control flow
OP_JF = 0x60
OP_JMP = 0x62
OP_RET = 0x66
OP_CALL = 0x68
OP_VOID_CALL = 0x69
OP_CALL_EXTERN = 0x6A
OP_VOID_CALL_EXTERN = 0x6B

# structs
OP_ALLOCA_STRUCT = 0x70
OP_SET_FIELD = 0x71
OP_LOAD_FIELD = 0x72
OP_IFIELD_INC = 0x73
OP_IFIELD_DEC = 0x74
OP_STORE_FIELD = 0x75

OP_ALLOCA_ARRAY = 0x79
OP_ARRAY_STORE = 0x7A
OP_ARRAY_SET = 0x7B
OP_ARRAY_GET = 0x7C

OP_LOG = 0x85

# TODO: replace with type_tag_matrix
optag_to_opcode = {
    OpTag.ADD: OP_IADD,
    OpTag.SUB: OP_ISUB,
    OpTag.MUL: OP_IMUL,
    OpTag.DIV: OP_IDIV,
    OpTag.MOD: OP_IREM,
    OpTag.AND: OP_IAND,
    OpTag.OR: OP_IOR,
    OpTag.BAND: OP_IBAND,
    OpTag.BOR: OP_IBOR,
    OpTag.BXOR: OP_IBXOR,
    OpTag.SHL: OP_ISHL,
    OpTag.SHR: OP_ISHR,
    OpTag.LT: OP_ILT,
    OpTag.LTE: OP_ILE,
    OpTag.GT: OP_IGT,
    OpTag.GTE: OP_IGE,
    OpTag.EQ: OP_IEQ,
    OpTag.NEQ: OP_INE,

    OpTag.Not: OP_BNOT,
}

bool_cast_table = {3: OP_I2B, 4: OP_L2B}
cast_table = {(3, 4): OP_I2L, (4, 3): OP_L2I, (2, 3): OP_B2I}


class FunctionIR:
    def __init__(self, function_id: int, name_idx: int, local_count: int, param_count: int, bytecode: bytes):
        self.function_id = function_id
        self.name_idx = name_idx
        self.bytecode = bytecode
        self.local_count = local_count
        self.param_count = param_count

    def serialize(self) -> bytes:
        result = bytearray()
        result += self.function_id.to_bytes(2, "little")
        result += self.name_idx.to_bytes(2, "little")
        result += self.param_count.to_bytes(2, "little")
        result += self.local_count.to_bytes(2, "little")
        result += len(self.bytecode).to_bytes(4, "little")
        result += self.bytecode
        return result


class IrModule:
    def __init__(self):
        self.const_table = []
        self.const_index_map = {}
        self.functions = []
        self.loop_start_indices = []
        self.loop_break_patches = []
        self.extern_lib_blocks: dict[str, dict[str, int | list[int]]] = {}
        self.main_function_index = 0

    def get_const_index(self, value) -> int:
        if value not in self.const_index_map:
            self.const_index_map[value] = len(self.const_table)
            self.const_table.append(value)
        return self.const_index_map[value]

    def compile_expr(self, expr, code: bytearray):
        if expr.kind == HirNodeTag.ConstInt:
            code.append(OP_LIC)
            idx = self.get_const_index(expr.val)
            code += idx.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.ConstStr:
            code.append(OP_LSC)
            idx = self.get_const_index(expr.val)
            code += idx.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.ConstBool:
            code.append(OP_LBT if expr.val == True else OP_LBF)
        elif expr.kind == HirNodeTag.VarRef:
            code.append(OP_LOAD)
            code += expr.symbol.local_offset.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.BoolCast:
            self.compile_expr(expr.expr, code)
            code.append(OP_I2B)
        elif expr.kind == HirNodeTag.Cast:
            self.compile_expr(expr.expr, code)
            code.append(cast_table[(expr.from_type, expr.to_type)])
        elif expr.kind == HirNodeTag.BinOp:
            self.compile_expr(expr.lhs, code)
            self.compile_expr(expr.rhs, code)
            code.append(optag_to_opcode[expr.op_tag])
        elif expr.kind == HirNodeTag.UnOp:
            op_map = {
                OpTag.PreIncrement: (OP_IINC, OP_IFIELD_INC),
                OpTag.PreDecrement: (OP_IDEC, OP_IFIELD_DEC),
                OpTag.PostIncrement: (OP_IINC, OP_IFIELD_INC),
                OpTag.PostDecrement: (OP_IDEC, OP_IFIELD_DEC),
            }

            if expr.op_tag in op_map:
                var_op, field_op = op_map[expr.op_tag]

                if expr.expr.kind == HirNodeTag.VarRef:
                    offset = expr.expr.symbol.local_offset.to_bytes(2, "little")
                    if expr.op_tag in (OpTag.PostIncrement, OpTag.PostDecrement):
                        code.append(OP_LOAD)
                        code += offset
                        code.append(var_op)
                        code += offset
                    else:
                        code.append(var_op)
                        code += offset
                        code.append(OP_LOAD)
                        code += offset
                else:
                    index = expr.expr.field_index.to_bytes(2, "little")
                    if expr.op_tag in (OpTag.PostIncrement, OpTag.PostDecrement):
                        code.append(OP_LOAD_FIELD)
                        code += index
                        code.append(field_op)
                        code += index
                    else:
                        code.append(field_op)
                        code += index
                        code.append(OP_LOAD_FIELD)
                        code += index
            else:
                self.compile_expr(expr.expr, code)
                code.append(optag_to_opcode[expr.op_tag])
        elif expr.kind == HirNodeTag.StoreField:
            self.compile_expr(expr.value, code)
            self.compile_expr(expr.obj, code)
            code.append(OP_STORE_FIELD)
            code += expr.field_index.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.Call:
            is_void_call = expr.type_id == TypeRegistry.VoidType
            for arg in expr.args:
                self.compile_expr(arg, code)
            if expr.function_symbol.linkage == Linkage.External:
                code.append(OP_VOID_CALL_EXTERN if is_void_call else OP_CALL_EXTERN)
                code += self.get_const_index(f"{expr.function_symbol.lib_prefix}_{expr.function_symbol.name}").to_bytes(
                    2,
                    "little")
            else:
                code.append(OP_VOID_CALL if is_void_call else OP_CALL)
                code += expr.function_symbol.function_id.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.CreateStruct:
            code.append(OP_ALLOCA_STRUCT)
            code += expr.num_fields.to_bytes(2, "little")
            for field in expr.values:
                self.compile_expr(field.value, code)
                code.append(OP_SET_FIELD)
                code += field.field_index.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.ArrayLiteral:
            code.append(OP_ALLOCA_ARRAY)
            code += len(expr.elements).to_bytes(2, "little")
            for i, ele in enumerate(expr.elements):
                self.compile_expr(ele, code)
                code.append(OP_ARRAY_SET)
                code += i.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.FieldAccess:
            self.compile_expr(expr.obj, code)
            code.append(OP_LOAD_FIELD)
            code += expr.field_index.to_bytes(2, "little")
        elif expr.kind == HirNodeTag.IndexedAccess:
            self.compile_expr(expr.container, code)
            self.compile_expr(expr.index, code)
            code.append(OP_ARRAY_GET)
        elif expr.kind == HirNodeTag.StoreIndexed:
            self.compile_expr(expr.obj.container, code)
            self.compile_expr(expr.obj.index, code)
            self.compile_expr(expr.value, code)
            code.append(OP_ARRAY_STORE)
        else:
            raise ValueError(f"Unsupported expression kind: {expr.kind}")

    def generate_bytecode_from_block(self, block: HirBlock, code: bytearray):
        for node in block.nodes:
            if node.kind == HirNodeTag.Return:
                if node.expr:
                    self.compile_expr(node.expr, code)
                code.append(OP_RET)

            elif node.kind == HirNodeTag.StoreLocal:
                self.compile_expr(node.value, code)
                code.append(OP_STORE)
                code += node.symbol.local_offset.to_bytes(2, "little")

            elif node.kind == HirNodeTag.Log:
                self.compile_expr(node.expr, code)
                code.append(OP_LOG)

            elif node.kind == HirNodeTag.Continue:
                code.append(OP_JMP)
                code += self.loop_start_indices[-1].to_bytes(2, "little")

            elif node.kind == HirNodeTag.Break:
                code.append(OP_JMP)
                self.loop_break_patches[-1].append(len(code))
                code += b"\x00\x00"

            elif node.kind == HirNodeTag.Branch:
                self.compile_expr(node.condition, code)
                code.append(OP_JF)
                jmp_patch = len(code)
                code += b"\x00\x00"

                self.generate_bytecode_from_block(node.then_block, code)

                if node.else_block:
                    code.append(OP_JMP)
                    merge_patch = len(code)
                    code += b"\x00\x00"
                    code[jmp_patch:jmp_patch + 2] = len(code).to_bytes(2, "little")

                    self.generate_bytecode_from_block(node.else_block, code)
                    code[merge_patch:merge_patch + 2] = len(code).to_bytes(2, "little")
                else:
                    code[jmp_patch:jmp_patch + 2] = len(code).to_bytes(2, "little")
            elif node.kind == HirNodeTag.MultiBranch:
                merge_patches = []
                for (condition, branch) in node.branches:
                    self.compile_expr(condition, code)
                    code.append(OP_JF)
                    cond_path_index = len(code)
                    code += b"\x00\x00"
                    self.generate_bytecode_from_block(branch, code)
                    code.append(OP_JMP)
                    merge_patches.append(len(code))
                    code += b"\x00\x00"
                    code[cond_path_index:cond_path_index + 2] = len(code).to_bytes(2, "little")

                if node.else_block:
                    self.generate_bytecode_from_block(node.else_block, code)

                for patch_idx in merge_patches:
                    code[patch_idx:patch_idx + 2] = len(code).to_bytes(2, "little")

            elif node.kind == HirNodeTag.LoopBlock:
                self.loop_start_indices.append(len(code))
                self.loop_break_patches.append([])
                self.generate_bytecode_from_block(node, code)
                code.append(OP_JMP)
                code += self.loop_start_indices[-1].to_bytes(2, "little")

                break_patches = self.loop_break_patches.pop()
                loop_end_idx = len(code)
                for patch_idx in break_patches:
                    code[patch_idx:patch_idx + 2] = loop_end_idx.to_bytes(2, "little")

                self.loop_start_indices.pop()

            elif node.kind in (HirNodeTag.Block, HirNodeTag.FunctionBlock):
                self.generate_bytecode_from_block(node, code)

            else:
                self.compile_expr(node, code)

    def add_function(self, func: FunctionBlock):
        name_idx = self.get_const_index(func.name)
        self.main_function_index = func.function_id if func.name == "main" else self.main_function_index
        code = bytearray()
        self.generate_bytecode_from_block(func, code)
        self.functions.append(FunctionIR(func.function_id, name_idx, func.local_count, len(func.symbol.params), code))

    def build(self, block):
        for node in block.nodes:
            if node.kind == HirNodeTag.ExternLibBlock:
                extern_block = {
                    "name": self.get_const_index(node.name),
                    "indices": []
                }
                for symbol in node.symbols:
                    extern_block["indices"].append(
                        self.get_const_index(f"{node.name}_{symbol}")
                    )
                self.extern_lib_blocks[node.name] = extern_block
            else:
                self.add_function(node)

    def emit(self) -> bytes:
        result = bytearray()

        result += b"PEXB"
        result += bytes(12)

        result += len(self.const_table).to_bytes(2, "little")
        for c in self.const_table:
            if isinstance(c, int):
                result.append(0x01)
                result += c.to_bytes(4, "little")
            elif isinstance(c, str):
                result.append(0x02)
                s_bytes = c.encode("utf-8")
                result += len(s_bytes).to_bytes(2, "little")
                result += s_bytes
            else:
                raise ValueError(f"Unsupported constant type: {type(c)}")

        result += self.main_function_index.to_bytes(2, "little")
        result += len(self.functions).to_bytes(2, "little")
        for f in self.functions:
            result += f.serialize()

        result += len(self.extern_lib_blocks).to_bytes(2, "little")
        for key in self.extern_lib_blocks:
            block = self.extern_lib_blocks[key]
            result += len(block["indices"]).to_bytes(2, "little")
            result += block["name"].to_bytes(2, "little")
            for idx in block["indices"]:
                result += idx.to_bytes(2, "little")

        return result
