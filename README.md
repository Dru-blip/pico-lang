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

#### Example

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
