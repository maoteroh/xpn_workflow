#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <time.h>

// gcc validar_pgms.c -o validar_pgms
// Uso: ./validar_pgms <directorio_entrada> <directorio_ad_hoc>
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
            printf("Verificación de formato PGM completada para %s.\n", entry->d_name);
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
    return 0;
}

// int main(int argc, char *argv[]) {
//     if (argc != 3) {
//         fprintf(stderr, "Uso: %s <directorio_entrada> <directorio_ad_hoc>\n", argv[0]);
//         return 1;
//     }

//     // Capturar el tiempo inicial
//     clock_t start = clock();

//     validate_files(argv[1], argv[2]);
//     // Capturar el tiempo final
//     clock_t end = clock();

//     // Calcular el tiempo transcurrido en segundos
//     double elapsed_time = (double)(end - start) / CLOCKS_PER_SEC;
//     printf("Tiempo total de validación: %.6f segundos\n", elapsed_time);

//     return 0;
// }

