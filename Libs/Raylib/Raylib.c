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
    pstr title = PICO_POP_STR(env->vm);
    pint height = PICO_POP_INT(env->vm);
    pint width = PICO_POP_INT(env->vm);

    InitWindow(width, height, title);
}

DEFINE_FN_VOID(close_window) { CloseWindow(); }

DEFINE_FN(window_should_close) {
    return WindowShouldClose() ? pico_true : pico_false;
}

DEFINE_FN_VOID(begin_drawing) { BeginDrawing(); }

DEFINE_FN_VOID(end_drawing) { EndDrawing(); }

DEFINE_FN_VOID(set_target_fps) { SetTargetFPS(PICO_POP_INT(env->vm)); }

DEFINE_FN_VOID(clear_background) {
    ClearBackground(valueToColor(PICO_POP_OBJ(env->vm)));
}

DEFINE_FN_VOID(draw_text) {
    Color color = valueToColor(PICO_POP_OBJ(env->vm));
    pint size = PICO_POP_INT(env->vm);
    pint y = PICO_POP_INT(env->vm);
    pint x = PICO_POP_INT(env->vm);
    pstr text = PICO_POP_STR(env->vm);
    DrawText(text, x, y, size, color);
}

PICO_EXPORT void pico_lib_Init(pico_env *env) {
    pico_register_native_void_function(env, "raylib_init_window",
                                       raylib_init_window);
    pico_register_native_void_function(env, "raylib_close_window",
                                       raylib_close_window);
    pico_register_native_function(env, "raylib_window_should_close",
                                  raylib_window_should_close);
    pico_register_native_void_function(env, "raylib_begin_drawing",
                                       raylib_begin_drawing);
    pico_register_native_void_function(env, "raylib_end_drawing",
                                       raylib_end_drawing);
    pico_register_native_void_function(env, "raylib_set_target_fps",
                                       raylib_set_target_fps);
    pico_register_native_void_function(env, "raylib_clear_background",
                                       raylib_clear_background);

    pico_register_native_void_function(env, "raylib_draw_text",
                                       raylib_draw_text);
}
