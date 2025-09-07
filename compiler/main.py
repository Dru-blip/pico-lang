from hirgen import HirGen
from ir import IrModule
from parser import Parser
from sema import Sema

if __name__ == '__main__':
    program = Parser.parse("test.pco", "fn main()void{let a=2;let b=3;log a+b*5-8/3;}")
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
