# Pico Language

Pico is a **statically typed programming language** that compiles down to bytecode, executed by a **bytecode interpreter / virtual machine (VM)**.

⚠️ **Note:** Pico is a learning project to explore how bytecode-interpreted languages work, how they manage memory, and how such languages interact with the outside world.

- **Compiler**: Written in Python
- **Runtime / VM**: Written in C
- **Garbage Collection**: Semi-space garbage collector
- **Extensibility**: Provides native interfaces to extend the language via libraries. The Pico VM can load and register native functions at load time from library files.
- **Statically typed**: Catch type errors at compile time.
- **Bytecode execution**: Programs compile to portable bytecode files.
- **Native function support**: Extend the language by writing libraries in C.
- **Garbage collected runtime**: Semi-space collector automatically manages memory.

## Example

Here's a simple example that creates a window using Raylib:

```pico
struct Color{
    int r;
    int g;
    int b;
    int a;
}

fn main()void{
    let COLOR_ORANGE=Color{ .r=255, .g=161, .b=0, .a=255 };
    let COLOR_WHITE=Color{.r=255, .g=255, .b=255, .a=255};
    raylib::init_window(800, 600, "Raylib Example");
    raylib::set_target_fps(60);
    loop{
        if(raylib::window_should_close()){
            break;
        }
        raylib::begin_drawing();
        raylib::clear_background(COLOR_ORANGE);
        raylib::draw_text("Congrats! You created your first window!", 190, 200, 20, COLOR_WHITE);
        raylib::end_drawing();
    }
    raylib::close_window();
    return;
}

/*
    raylib functions
*/
extern @prefix="raylib"{
    // windowing functions
    fn init_window(int width, int height, str title)void;
    fn close_window()void;
    fn window_should_close()bool;
    // drawing functions
    fn begin_drawing()void;
    fn end_drawing()void;
    fn set_target_fps(int fps)void;
    fn clear_background(Color color)void;
    // text functions
    fn draw_text(str text, int posX, int posY, int fontSize,Color color)void;
}
```

## Getting Pico

Currently, Pico provides prebuilt binaries for **Linux x86-64 only**. Support for other platforms has been planned. You can get Pico either by **downloading prebuilt binaries** or by **compiling from source**.

---

### Option 1: Download Prebuilt Binaries (Linux x86-64)

The easiest way is to use the **precompiled Pico VM and example programs**.

**Download binaries:**
[pico_x86-64_linux.zip](https://github.com/Dru-blip/pico-lang/releases)

Extract the zip file.

**Contents of zip file:**

- `picoc` (executable for compiler)
- `pico` (executable containing runtime)
- `libraylib.so` (library containing raylib functions)
- `libpio.so` (library containing io functions)

Place the `.so` files in a directory of your choice.
See **Usage** section to compile and run programs.

### Option 2: Compile from Source

If you want to compile Pico from source, you can follow these steps:

Make sure you have the following prerequisites installed:

- make
- gcc/clang versions which can compiler c23 standard
- Python 3.12.3 (version im using to build pico compiler)
- raylib (to run the example pico) can download prebuild native library from releases page or see [raylib documentation](https://www.raylib.com/)

1. Clone the Pico repository:

   ```bash
   git clone https://github.com/Dru-blip/pico-lang.git
   ```

2. Navigate to the project directory:

   ```bash
   cd pico-lang
   ```

3. Build the project using Make:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install pyinstaller typer
   make
   ```

   Make will create two directories: `out` and `dist`. The `out` directory contains the pico runtime (`pico`), while the `dist` directory contains the pico compiler (`picoc`).

## Usage

**Compile a Pico source file (`.pic`) into bytecode (`.pbc`):**

By default, the compiler will emit an `out.pbc` file in the current directory.

```bash
# Current implementation only supports single file compilation
./picoc <filename>.pico
```

For running a pico bytecode file:

```bash
pico <*.pbc> <path to libs>

# Example
pico out.pbc ./lib
```

## Language Syntax and Features

This section documents the currently implemented syntax and features of Pico.
It is a work-in-progress and grows as new features are added to the compiler and VM.

### 1. Program Structure

A Pico program consists of:

- Struct definitions
- Function definitions
- Extern library declarations

### 2. Types

Primitive Types:

- `bool`
- `int`
- `str`
- `void`

Struct Types:

these are user defined types , declared with `struct` keyword

```
struct Color {
    int r;
    int g;
    int b;
    int a;
}
```

instances can be created with field initializers

```
let c = Color{ .r=255, .g=161, .b=0, .a=255 };
```

struct instances by default are heap allocated and garbage collected user does not have to worry about memory management.
every field has to be initialized, compiler will not throw any error if not initialized,
access them at runtime can cause UB(undefined behavior) or could crash the program.

struct fields are accessed with `.` operator

```
let c = Color{ .r=255, .g=161, .b=0, .a=255 };
log c.r;
```

### 3.Variables

declared using `let` keyword

```
let x:int = 10;
let message = "Hello"; (type inference)
```

Must be initialized at declaration.
if type specifier is missing, compiler will automatically infer the type from the initializer during semantic analysis.

### 4.Functions

declared using `fn` keyword

```
fn add(int a, int b) int {
    return a + b;
}
```

parameter types and return type specifiers are mandatory.

### 5.Functions

1.Loops

- infinite loop

```
loop {
    // iterate forever
}
```

- while loop

```
    let a=1;
    while(a<20){
        a=a+1;
    }
    log a;
```

2.If else

```
if condition {
    // code block
} else {
    // code block
}
```

### 6.Casting

type casting is done using `as` keyword

```
let x = 10 as float;
```

### 7.Namespaces & External Libraries

External functions are declared in extern blocks:

```
extern @prefix="raylib" {
    fn init_window(int width, int height, str title) void;
}

```

Functions are accessed with prefix::function

```
raylib::init_window(800, 600, "Hello");
```
