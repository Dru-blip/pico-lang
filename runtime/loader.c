
#include "pico.h"
#include "stb_ds.h"
#include <stdio.h>
#include <stdlib.h>

#define HEADER_SIZE 16

static const bool check_file_ext(const char *filename, const char *ext) {
    const char *dot = strrchr(filename, '.');
    if (!dot || dot == filename)
        return false;
    return strcmp(dot + 1, ext) == 0;
}

bytecode_unit load_bytecode(const char *filename) {
    if (!check_file_ext(filename, "pbc")) {
        fprintf(stderr, "Error: Invalid file extension for '%s'\n", filename);
        exit(EXIT_FAILURE);
    }
    FILE *file = fopen(filename, "rb");

    if (!file) {
        fprintf(stderr, "Error: Unable to open file '%s'\n", filename);
        exit(EXIT_FAILURE);
    }

    // skipping over header
    pbyte header[HEADER_SIZE];
    fread(header, sizeof(pbyte), HEADER_SIZE, file);

    // load constants
    pbyte num_constants_bytes[2];
    fread(&num_constants_bytes, sizeof(pbyte), 2, file);
    pico_value *constants = nullptr;

    puint num_constants =
        num_constants_bytes[0] | (num_constants_bytes[1] << 8);

    pint constants_read = 0;
    while (constants_read < num_constants) {
        pbyte tag;
        fread(&tag, sizeof(pbyte), 1, file);
        if (tag == 0x01) {
            // if int
            // read 4 bytes
            pbyte value[4];
            fread(&value, sizeof(pbyte), 4, file);
            pint constant = value[0] | (value[1] << 8) | (value[2] << 16) |
                            (value[3] << 24);

            arrput(constants, TO_PICO_INT(constant));
        } else if (tag == 0x02) {
            pbyte len_bytes[2];
            fread(&len_bytes, sizeof(pbyte), 2, file);
            puint len = len_bytes[0] | (len_bytes[1] << 8);

            pstr str = malloc(len + 1);
            fread(str, sizeof(pbyte), len, file);
            str[len] = '\0';
            arrput(constants, TO_PICO_STR(str, len));
        }
        constants_read++;
    }

    // main function index
    pbyte main_function_index_bytes[2];
    fread(&main_function_index_bytes, sizeof(pbyte), 2, file);
    puint main_function_index =
        main_function_index_bytes[0] | (main_function_index_bytes[1] << 8);

    // read functions
    pbyte num_functions_bytes[2];
    fread(&num_functions_bytes, sizeof(pbyte), 2, file);
    puint num_functions =
        num_functions_bytes[0] | (num_functions_bytes[1] << 8);

    pico_function *functions = nullptr;
    arrsetlen(functions, num_functions);

    for (puint i = 0; i < num_functions; i++) {
        // read function index
        pbyte index_bytes[2];
        fread(&index_bytes, sizeof(pbyte), 2, file);
        puint function_index = index_bytes[0] | (index_bytes[1] << 8);

        // read function name id
        pbyte name_id_bytes[2];
        fread(&name_id_bytes, sizeof(pbyte), 2, file);
        puint name_id = name_id_bytes[0] | (name_id_bytes[1] << 8);

        pbyte param_bytes[2];
        fread(&param_bytes, sizeof(pbyte), 2, file);
        puint param_count = param_bytes[0] | (param_bytes[1] << 8);

        pbyte local_bytes[2];
        fread(&local_bytes, sizeof(pbyte), 2, file);
        puint local_count = local_bytes[0] | (local_bytes[1] << 8);

        // read function code length
        pbyte code_len_bytes[4];
        fread(&code_len_bytes, sizeof(pbyte), 4, file);
        puint code_len = code_len_bytes[0] | (code_len_bytes[1] << 8) |
                         (code_len_bytes[2] << 16) | (code_len_bytes[3] << 24);

        // read function code
        pbyte *code = malloc(code_len);
        fread(code, sizeof(pbyte), code_len, file);
        pico_function function = {.code = code,
                                  .name_id = name_id,
                                  .code_len = code_len,
                                  .local_count = local_count,
                                  .param_count = param_count};
        functions[function_index] = function;
    }

    // read extern libs
    pbyte lib_count[2];
    fread(&lib_count, sizeof(pbyte), 2, file);
    puint num_libs = lib_count[0] | (lib_count[1] << 8);

    for (puint i = 0; i < num_libs; i++) {
        // lib name
        pbyte name_index_bytes[2];
        fread(&name_index_bytes, sizeof(pbyte), 2, file);
        puint name_index = name_index_bytes[0] | (name_index_bytes[1] << 8);

        // functions count
        pbyte lib_function_bytes[2];
        fread(&lib_function_bytes, sizeof(pbyte), 2, file);
        puint lib_fuctions_count =
            lib_function_bytes[0] | (lib_function_bytes[1] << 8);

        for (puint j = 0; j < lib_fuctions_count; j++) {
            pbyte lib_function_name_bytes[2];
            fread(&lib_function_name_bytes, sizeof(pbyte), 2, file);
            // function name index
            puint lib_function_name_index =
                lib_function_name_bytes[0] | (lib_function_name_bytes[1] << 8);
        }
    }

    fclose(file);
    return (bytecode_unit){
        .main_function_index = main_function_index,
        .constants = constants,
        .functions = functions,
    };
}
