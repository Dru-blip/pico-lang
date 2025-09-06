from hirgen import HirGen
from parser import Parser

if __name__ == '__main__':
    program = Parser.parse("test.pco", "fn main()void{return 5;} fn add()int{return 5;}")
    block = HirGen(program).generate()
