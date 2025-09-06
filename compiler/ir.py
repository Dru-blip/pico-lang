from hir import FunctionBlock, HirBlock, ConstInt, Return

OP_LIC = 0x05
OP_RET = 0x66


class FunctionIR:
    def __init__(self, name_idx: int, bytecode: bytes):
        self.name_idx = name_idx
        self.bytecode = bytecode

    def serialize(self) -> bytes:
        result = bytearray()
        result += self.name_idx.to_bytes(2, "little")
        result += len(self.bytecode).to_bytes(4, "little")
        result += self.bytecode
        return result


class IrModule:
    def __init__(self):
        self.const_table = []
        self.const_index_map = {}
        self.functions = []

    def get_const_index(self, value) -> int:
        if value not in self.const_index_map:
            self.const_index_map[value] = len(self.const_table)
            self.const_table.append(value)
        return self.const_index_map[value]

    def compile_expr(self, expr) -> bytearray:
        code = bytearray()
        if isinstance(expr, ConstInt):
            code.append(OP_LIC)
            idx = self.get_const_index(expr.val)
            code += idx.to_bytes(2, "little")
        return code

    def generate_bytecode_from_block(self, block: HirBlock) -> bytearray:
        code = bytearray()
        for node in block.nodes:
            if isinstance(node, Return):
                code += self.compile_expr(node.expr)
                code.append(OP_RET)
            elif isinstance(node, HirBlock):
                code += self.generate_bytecode_from_block(node)
        return code

    def add_function(self, func: FunctionBlock):
        name_idx = self.get_const_index(func.name)

        bytecode = self.generate_bytecode_from_block(func)
        self.functions.append(FunctionIR(name_idx, bytecode))

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

        result += len(self.functions).to_bytes(2, "little")
        for f in self.functions:
            result += f.serialize()
        return result
