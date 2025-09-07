from hirgen import HirGen
from ir import IrModule
from parser import Parser

if __name__ == '__main__':
    program = Parser.parse("test.pco", "fn main()void{log 2>>3;}")
    block = HirGen(program).generate()
    module = IrModule()

    for fb in block.nodes:
        module.add_function(fb)

    binary = module.emit()

    print("Global Constant Table:", module.const_table)
    print("Binary:", list(binary))
    with open("out.pbc", "wb") as f:
        f.write(binary)
