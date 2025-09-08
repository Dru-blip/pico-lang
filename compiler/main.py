import typer

from hirgen import HirGen
from ir import IrModule
from parser import Parser
from sema import Sema


# TODO: while and for loops.
# TODO: increment and decrement operators.
# TODO: Compound assignments.
# TODO: Ternary expressions
# TODO: switch statements
# TODO: signed integers.
def main(filename: str):
    with open(filename) as f:
        source = f.read()

    program = Parser.parse(filename, source)
    block = HirGen(program).generate()
    Sema(block).analyze()
    module = IrModule()
    #
    for fb in block.nodes:
        module.add_function(fb)
    #
    binary = module.emit()

    print("Global Constant Table:", module.const_table)
    print("Binary:", list(binary))
    with open("out.pbc", "wb") as f:
        f.write(binary)


if __name__ == '__main__':
    typer.run(main)
