#define _POSIX_C_SOURCE 200809L

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

static double seconds(void)
{
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return (double)value.tv_sec + (double)value.tv_nsec / 1e9;
}

static double walk(unsigned char *memory, size_t bytes, size_t stride, int rounds)
{
    volatile uint64_t sum = 0;
    const double start = seconds();
    for (int round = 0; round < rounds; ++round) {
        for (size_t offset = 0; offset < bytes; offset += stride) {
            sum += memory[offset];
        }
    }
    const double elapsed = seconds() - start;
    if (sum == UINT64_MAX) {
        puts("невозможное значение");
    }
    return elapsed;
}

int main(void)
{
    const size_t bytes = 128U * 1024U * 1024U;
    const long page_size = sysconf(_SC_PAGESIZE);
    unsigned char *memory = calloc(bytes, 1);
    if (memory == NULL || page_size <= 0) {
        perror("allocation");
        free(memory);
        return 1;
    }

    const double cache_friendly = walk(memory, bytes, 64, 4);
    const double page_stride = walk(memory, bytes, (size_t)page_size, 400);
    printf("page size: %ld bytes\n", page_size);
    printf("stride 64 bytes: %.6f s\n", cache_friendly);
    printf("stride page size: %.6f s\n", page_stride);
    puts("Для точного числа TLB misses в Linux: perf stat -e dTLB-load-misses ./tlb_stride");
    free(memory);
    return 0;
}
