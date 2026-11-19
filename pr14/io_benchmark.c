#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static double seconds(void) {
    struct timespec value;
    if (clock_gettime(CLOCK_MONOTONIC, &value) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (double)value.tv_sec + (double)value.tv_nsec / 1e9;
}

static void fill(unsigned char *buffer, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        buffer[i] = (unsigned char)(i * 31U + 7U);
    }
}

static double write_syscalls(const char *path, size_t total, size_t block) {
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) { perror("open"); exit(EXIT_FAILURE); }
    unsigned char *buffer = malloc(block);
    if (buffer == NULL) { perror("malloc"); exit(EXIT_FAILURE); }
    fill(buffer, block);
    double start = seconds();
    for (size_t done = 0; done < total;) {
        size_t amount = total - done < block ? total - done : block;
        ssize_t written = write(fd, buffer, amount);
        if (written < 0) { perror("write"); exit(EXIT_FAILURE); }
        done += (size_t)written;
    }
    if (fsync(fd) != 0) { perror("fsync"); exit(EXIT_FAILURE); }
    double elapsed = seconds() - start;
    free(buffer);
    close(fd);
    unlink(path);
    return elapsed;
}

static double write_stdio(const char *path, size_t total, size_t block) {
    FILE *file = fopen(path, "wb");
    if (file == NULL) { perror("fopen"); exit(EXIT_FAILURE); }
    unsigned char *buffer = malloc(block);
    if (buffer == NULL) { perror("malloc"); exit(EXIT_FAILURE); }
    fill(buffer, block);
    double start = seconds();
    for (size_t done = 0; done < total;) {
        size_t amount = total - done < block ? total - done : block;
        if (fwrite(buffer, 1, amount, file) != amount) { perror("fwrite"); exit(EXIT_FAILURE); }
        done += amount;
    }
    if (fflush(file) != 0 || fsync(fileno(file)) != 0) { perror("flush"); exit(EXIT_FAILURE); }
    double elapsed = seconds() - start;
    free(buffer);
    fclose(file);
    unlink(path);
    return elapsed;
}

int main(int argc, char **argv) {
    size_t mebibytes = 16;
    if (argc == 2) {
        char *end = NULL;
        unsigned long value = strtoul(argv[1], &end, 10);
        if (end == argv[1] || *end != '\0' || value == 0 || value > 1024) {
            fprintf(stderr, "Использование: %s [МиБ, 1..1024]\n", argv[0]);
            return EXIT_FAILURE;
        }
        mebibytes = (size_t)value;
    }
    size_t total = mebibytes * 1024U * 1024U;
    double one = write_syscalls("io-byte.bin", total, 1);
    double block = write_syscalls("io-block.bin", total, 64U * 1024U);
    double stdio = write_stdio("io-stdio.bin", total, 64U * 1024U);
    printf("Объём: %zu МиБ\n", mebibytes);
    printf("write по 1 байту: %.3f с\n", one);
    printf("write по 64 КиБ:  %.3f с\n", block);
    printf("fwrite по 64 КиБ: %.3f с\n", stdio);
    printf("Ускорение блоками: %.1fx\n", one / block);
    return EXIT_SUCCESS;
}
