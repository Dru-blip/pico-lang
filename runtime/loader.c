#include "loader.h"
#include "pico.h"
#include "stb_ds.h"
#include <stdio.h>
#include <stdlib.h>

#define HEADER_SIZE 16

bytecode_unit load_bytecode(const char *filename) {
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

    // read functions
    pbyte num_functions_bytes[2];
    fread(&num_functions_bytes, sizeof(pbyte), 2, file);
    puint num_functions =
        num_functions_bytes[0] | (num_functions_bytes[1] << 8);

    pico_function *functions = nullptr;

    for (puint i = 0; i < num_functions; i++) {
        // read function name id
        pbyte name_id_bytes[2];
        fread(&name_id_bytes, sizeof(pbyte), 2, file);
        puint name_id = name_id_bytes[0] | (name_id_bytes[1] << 8);

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
                                  .local_count = local_count};
        arrput(functions, function);
    }

    fclose(file);
    return (bytecode_unit){
        .constants = constants,
        .functions = functions,
    };
}
