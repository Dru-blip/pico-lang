from hirgen import HirGen
from ir import IrModule
from parser import Parser
from sema import Sema


# TODO: Compound assignments.
# TODO: Ternary expressions
def main():
    with open("test.pco") as f:
        source = f.read()

    program = Parser.parse("test.pco", source)
    block = HirGen(program).generate()
    Sema(block).analyze()
    module = IrModule()

    for fb in block.nodes:
        module.add_function(fb)

    binary = module.emit()

    print("Global Constant Table:", module.const_table)
    print("Binary:", list(binary))
    with open("out.pbc", "wb") as f:
        f.write(binary)


if __name__ == '__main__':
    main()
