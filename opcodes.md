#### load and stores
```text
Opcode(id=0x05){
    name = OP_LIC
    description = "Load an integer constant from the constant pool onto the stack"
    bytesize = 3
    operands = 1
}

Opcode(id=0x06){
    name = OP_LSC
    description = "Load a string constant from the constant pool onto the stack"
    bytesize = 3
    operands = 1
}

Opcode(id=0x07){
    name = OP_LBT
    description = "Push the boolean value true onto the stack"
    bytesize = 1
    operands = 0
}

Opcode(id=0x08){
    name = OP_LBF
    description = "Push the boolean value false onto the stack"
    bytesize = 1
    operands = 0
}

Opcode(id=0x09){
    name = OP_STORE
    description = "Store the top value from the stack into a variable"
    bytesize = 3
    operands = 1
}

Opcode(id=0x0A){
    name = OP_ISTORE
    description = "Store the top integer value from the stack into a variable"
    bytesize = 3
    operands = 1
}

Opcode(id=0x0B){
    name = OP_ILOAD
    description = "Load an integer variable onto the stack"
    bytesize = 3
    operands = 1
}

Opcode(id=0x0C){
    name = OP_LOAD
    description = "Load a variable (any type) onto the stack"
    bytesize = 3
    operands = 1
}

```

#### integer arithmetic

```
Opcode(id=0x20){
    name = OP_IADD
    description = "Pop two integers from the stack, add them, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x21){
    name = OP_ISUB
    description = "Pop two integers from the stack, subtract the second from the first, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x22){
    name = OP_IMUL
    description = "Pop two integers from the stack, multiply them, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x23){
    name = OP_IDIV
    description = "Pop two integers from the stack, divide the first by the second, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x24){
    name = OP_IREM
    description = "Pop two integers from the stack, compute the remainder of the division, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x25){
    name = OP_IAND
    description = "Pop two integers from the stack, compute logical AND, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x26){
    name = OP_IOR
    description = "Pop two integers from the stack, compute logical OR, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x27){
    name = OP_IBAND
    description = "Pop two integers from the stack, compute bitwise AND, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x28){
    name = OP_IBOR
    description = "Pop two integers from the stack, compute bitwise OR, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x29){
    name = OP_IBXOR
    description = "Pop two integers from the stack, compute bitwise XOR, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2A){
    name = OP_ISHL
    description = "Pop two integers from the stack, shift left, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2B){
    name = OP_ISHR
    description = "Pop two integers from the stack, shift right, and push the result"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2C){
    name = OP_IEQ
    description = "Pop two integers from the stack, compare for equality, push result as boolean"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2D){
    name = OP_INE
    description = "Pop two integers from the stack, compare for inequality, push result as boolean"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2E){
    name = OP_ILT
    description = "Pop two integers from the stack, compare if first < second, push result as boolean"
    bytesize = 1
    operands = 0
}

Opcode(id=0x2F){
    name = OP_ILE
    description = "Pop two integers from the stack, compare if first <= second, push result as boolean"
    bytesize = 1
    operands = 0
}

Opcode(id=0x30){
    name = OP_IGT
    description = "Pop two integers from the stack, compare if first > second, push result as boolean"
    bytesize = 1
    operands = 0
}

Opcode(id=0x31){
    name = OP_IGE
    description = "Pop two integers from the stack, compare if first >= second, push result as boolean"
    bytesize = 1
    operands = 0
}
```

#### type conversions

```
Opcode(id=0x5B){
    name = OP_L2B
    description = "Convert a long value to boolean and push onto stack"
    bytesize = 1
    operands = 0
}

Opcode(id=0x5C){
    name = OP_L2I
    description = "Convert a long value to integer and push onto stack"
    bytesize = 1
    operands = 0
}

Opcode(id=0x5D){
    name = OP_I2L
    description = "Convert an integer value to long and push onto stack"
    bytesize = 1
    operands = 0
}

Opcode(id=0x5E){
    name = OP_I2B
    description = "Convert an integer value to boolean and push onto stack"
    bytesize = 1
    operands = 0
}

```

#### control flow

```
Opcode(id=0x60){
    name = OP_JF
    description = "Jump to the target address if the top of stack is false"
    bytesize = 3
    operands = 1
}

Opcode(id=0x62){
    name = OP_JMP
    description = "Unconditionally jump to the target address"
    bytesize = 3
    operands = 1
}

Opcode(id=0x66){
    name = OP_RET
    description = "Return from the current function"
    bytesize = 1
    operands = 0
}

Opcode(id=0x68){
    name = OP_CALL
    description = "Call a function with the given index from the function table"
    bytesize = 3
    operands = 1
}

Opcode(id=0x69){
    name = OP_VOID_CALL
    description = "Call a function that does not return a value"
    bytesize = 3
    operands = 1
}

Opcode(id=0x6A){
    name = OP_CALL_EXTERN
    description = "Call an external library function"
    bytesize = 3
    operands = 1
}

Opcode(id=0x6B){
    name = OP_VOID_CALL_EXTERN
    description = "Call an external library function that does not return a value"
    bytesize = 3
    operands = 1
}

```

#### struct operations

```
Opcode(id=0x70){
    name = OP_ALLOCA_STRUCT
    description = "Allocate memory for a struct and push reference onto stack"
    bytesize = 3
    operands = 1
}

Opcode(id=0x71){
    name = OP_SET_FIELD
    description = "Set the value of a field in a struct reference"
    bytesize = 3
    operands = 1
}

Opcode(id=0x72){
    name = OP_LOAD_FIELD
    description = "Load the value of a field from a struct reference onto stack"
    bytesize = 3
    operands = 1
}

```

#### debugging

```
Opcode(id=0x85){
    name = OP_LOG
    description = "Pop the top value from the stack and log it for debugging"
    bytesize = 1
    operands = 0
}

```
