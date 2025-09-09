import typer

from hirgen import HirGen
from ir import IrModule
from parser import Parser
from pico_error import PicoError
from sema import Sema
from tokenizer import Token


def get_source_line(source, line_start, start):
    offset = start
    while offset < len(source) and source[offset] != '\n':
        offset += 1
    return source[line_start:offset]


def print_error(source: str, origin: Token, message: str):
    source_line = get_source_line(source, origin.line_start, origin.loc.start)

    print(f"Error: {message}")
    print(f"--> test.fl:{origin.loc.line}:{origin.loc.col}")
    print("  |")
    print(f"{origin.loc.line} | {source_line}")
    print("  |", end="")
    print(" " * origin.loc.col, end="")
    print("^" * (origin.loc.end - origin.loc.start))
    print("  |")


# TODO: while and for loops.
# TODO: increment and decrement operators.
# TODO: Compound assignments.
# TODO: Ternary expressions
# TODO: switch statements
# TODO: signed integers.
def main(filename: str):
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
    except PicoError as pse:
        print_error(source, pse.origin, pse.msg)


if __name__ == '__main__':
    # main("test.pco")
    typer.run(main)
