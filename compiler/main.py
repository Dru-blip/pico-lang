import typer

from error_printer import ErrorPrinter
from hirgen import HirGen
from ir import IrModule
from parser import Parser
from pico_error import PicoError
from sema import Sema


# TODO: type cast
# TODO: emit type descriptors in bytecode.
# TODO: introduce nil type.
# TODO: while and for loops.
# TODO: else if and switch statements.
# TODO: increment and decrement operators.
# TODO: logical not operator.
# TODO: Compound assignments.
# TODO: Ternary expressions
# TODO: unsigned integers,remaining signed integers(long,byte,char,byte).
def main(filename: str):
    if not filename.endswith(".pic"):
        print("invalid file extension, pico source files should have .pic as extension")
    else:
        with open(filename) as f:
            source = f.read()
        try:
            program = Parser.parse(filename, source)
            block = HirGen(program).generate()
            Sema(block).analyze()
            module = IrModule()
            module.build(block)
            binary = module.emit()

            # print("Global Constant Table:", module.const_table)
            # print("Binary:", list(binary))
            with open("out.pbc", "wb") as f:
                f.write(binary)
        except PicoError as pe:
            ErrorPrinter.print_error(source, pe.origin, pe.msg)


if __name__ == '__main__':
    # main("test.pic")
    typer.run(main)
