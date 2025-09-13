#include "pico.h"
#include <raylib.h>

#define DEFINE_FN(name) PICO_LIB_FN(raylib_, name)
#define DEFINE_FN_VOID(name) PICO_LIB_FN_VOID(raylib_, name)

static Color valueToColor(pico_object *obj) {
    return (Color){.r = PICO_OBJECT_GET_INT_FIELD(obj, 0),
                   .g = PICO_OBJECT_GET_INT_FIELD(obj, 1),
                   .b = PICO_OBJECT_GET_INT_FIELD(obj, 2),
                   .a = PICO_OBJECT_GET_INT_FIELD(obj, 3)};
}

DEFINE_FN_VOID(init_window) {
    pint width = GET_ARG_INT(args, 0);
    pint height = GET_ARG_INT(args, 1);
    pstr title = GET_ARG_STR(args, 2);

    InitWindow(width, height, title);
}

DEFINE_FN_VOID(close_window) { CloseWindow(); }

DEFINE_FN(window_should_close) {
    return WindowShouldClose() ? pico_true : pico_false;
}

DEFINE_FN_VOID(begin_drawing) { BeginDrawing(); }

DEFINE_FN_VOID(end_drawing) { EndDrawing(); }

DEFINE_FN_VOID(set_target_fps) { SetTargetFPS(GET_ARG_INT(args, 0)); }

DEFINE_FN_VOID(clear_background) {
    ClearBackground(valueToColor(GET_ARG_OBJ(args, 0)));
}

DEFINE_FN_VOID(draw_text) {
    pstr text = GET_ARG_STR(args, 0);
    pint x = GET_ARG_INT(args, 1);
    pint y = GET_ARG_INT(args, 2);
    pint size = GET_ARG_INT(args, 3);
    Color color = valueToColor(GET_ARG_OBJ(args, 4));
    DrawText(text, x, y, size, color);
}

PICO_EXPORT void pico_lib_Init(pico_env *env) {
    pico_register_native_void_function(env, "raylib_init_window", 3,
                                       raylib_init_window);
    pico_register_native_void_function(env, "raylib_close_window", 0,
                                       raylib_close_window);
    pico_register_native_function(env, "raylib_window_should_close", 0,
                                  raylib_window_should_close);
    pico_register_native_void_function(env, "raylib_begin_drawing", 0,
                                       raylib_begin_drawing);
    pico_register_native_void_function(env, "raylib_end_drawing", 0,
                                       raylib_end_drawing);
    pico_register_native_void_function(env, "raylib_set_target_fps", 1,
                                       raylib_set_target_fps);
    pico_register_native_void_function(env, "raylib_clear_background", 1,
                                       raylib_clear_background);

    pico_register_native_void_function(env, "raylib_draw_text", 5,
                                       raylib_draw_text);
}
