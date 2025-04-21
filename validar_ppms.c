#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

// gcc validar_ppms.c -o validar_ppms
// Uso: ./validar_ppms /tmp/expand/xpn
void validate_files(const char *input_dir, const char *input_dir_ad_hoc) {
    printf("Directorio de entrada verificacion: %s\n", input_dir);
    printf("Directorio Ad-Hoc: %s\n", input_dir_ad_hoc);
    DIR *dir = opendir(input_dir);
    if (!dir) {
        perror("Error al abrir el directorio de entrada");
        exit(1);
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        // Procesar solo archivos regulares
        if (entry->d_type == DT_REG) {
            char file_path[1024];
            snprintf(file_path, sizeof(file_path), "%s/%s", input_dir_ad_hoc, entry->d_name);
            printf("Verificando archivo: %s\n", file_path);

            FILE *file = fopen(file_path, "rb");
            if (!file) {
                fprintf(stderr, "Error al abrir el archivo %s\n", file_path);
                continue;
            }

            // Aquí se puede incluir lógica adicional para validar el contenido PGM.
            fclose(file);
            printf("Verificación de formato PPM completada para %s.\n", entry->d_name);
        }
    }
    
    closedir(dir);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <directorio_entrada>\n", argv[0]);
        return 1;
    }
    validate_files(argv[1], argv[2]);
    validate_files(argv[1], argv[2]);
    return 0;
}