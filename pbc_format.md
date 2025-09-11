### this document describes the pico bytecode file format

```
PCB{
  header: Header
  main_function:MainFunction
  constants:Constants
  functions:Functions
  libraries:Libraries // currently ignored by loader(reserved for future use)
}

Header{
  bytes[16] // Reserved metadata , currently ignored by loader
}

MainFunction{
    index: uint16            // Index into functions array
}

Constants{
    num_constants: uint16,   // Number of constants
    entries: ConstantEntry[num_constants]
}

ConstantEntry{
    tag: byte,               // 0x01 = int, 0x02 = string
    value: IntConstant | StringConstant
}

IntConstant{
  int32: little-endian     // 4-byte integer
}

StringConstant{
    length: uint16,          // Length of the string
    bytes[length]            // string bytes
}


Functions{
    num_functions: uint16,   // Number of functions
    entries: Function[num_functions]
}

Function{
    index: uint16,           // Function index
    name_id: uint16,         // Constant pool index for function name
    param_count: uint16,     // Number of parameters
    local_count: uint16,     // Number of local variables
    code_len: uint32,        // Length of function bytecode
    code: byte[code_len]     // Raw bytecode instructions
}

Libraries{
    num_libs: uint16,        // Number of external libraries
    entries: Library[num_libs]
}

Library{
    name_id: uint16,         // Constant pool index for library name
    num_functions: uint16,   // Number of functions in this library
    functions: LibFunction[num_functions]
}

LibFunction{
    name_id: uint16          // Constant pool index for function name
}

```
