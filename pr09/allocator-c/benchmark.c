#define _GNU_SOURCE

#include "my_alloc.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

#define REGION_SIZE (128U * 1024U * 1024U)

static int custom_allocator;
static size_t failures;
static my_allocator_stats snapshot;

static void *allocate_memory(size_t size)
{
    void *pointer;

    if (custom_allocator) {
        pointer = my_malloc(size);
    } else {
        pointer = malloc(size);
    }

    if (pointer == NULL) {
        ++failures;
    }

    return pointer;
}

static void release_memory(void *pointer)
{
    if (custom_allocator) {
        my_free(pointer);
    } else {
        free(pointer);
    }
}

static void *resize_memory(void *pointer, size_t size)
{
    void *result;

    if (custom_allocator) {
        result = my_realloc(pointer, size);
    } else {
        result = realloc(pointer, size);
    }

    if (result == NULL && size != 0) {
        ++failures;
    }

    return result;
}

static double elapsed_ms(
    struct timespec start,
    struct timespec finish
)
{
    double seconds =
        (double)(finish.tv_sec - start.tv_sec) * 1000.0;

    double nanoseconds =
        (double)(finish.tv_nsec - start.tv_nsec)
        / 1000000.0;

    return seconds + nanoseconds;
}

static long peak_rss_kb(void)
{
    struct rusage usage;

    if (getrusage(RUSAGE_SELF, &usage) != 0) {
        return -1;
    }

    return usage.ru_maxrss;
}

static void remember_stats(void)
{
    if (custom_allocator) {
        snapshot = my_allocator_get_stats();
    }
}

/* Сценарий 1: много небольших выделений. */
static void scenario_small(void)
{
    const size_t count = 50000;

    void **pointers =
        calloc(count, sizeof(*pointers));

    if (pointers == NULL) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }

    for (size_t i = 0; i < count; ++i) {
        size_t size =
            8U + (i * 37U) % 121U;

        pointers[i] =
            allocate_memory(size);

        if (pointers[i] != NULL) {
            memset(
                pointers[i],
                (int)(i & 0xffU),
                size
            );
        }
    }

    /* Заодно проверяем realloc. */
    for (size_t i = 0; i < count; i += 10U) {
        if (pointers[i] != NULL) {
            size_t new_size =
                160U + i % 128U;

            void *resized =
                resize_memory(
                    pointers[i],
                    new_size
                );

            if (resized != NULL) {
                pointers[i] = resized;

                memset(
                    pointers[i],
                    0x5a,
                    new_size
                );
            }
        }
    }

    /* Создаём фрагментацию. */
    for (size_t i = 0; i < count; i += 3U) {
        release_memory(pointers[i]);
        pointers[i] = NULL;
    }

    remember_stats();

    for (size_t i = 0; i < count; ++i) {
        release_memory(pointers[i]);
    }

    free(pointers);
}

/* Сценарий 2: постоянное чередование alloc/free. */
static void scenario_alternating(void)
{
    const size_t slots = 4096;
    const size_t operations = 100000;

    void **pointers =
        calloc(slots, sizeof(*pointers));

    if (pointers == NULL) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }

    for (size_t i = 0; i < operations; ++i) {
        size_t index =
            (i * 2654435761U) % slots;

        if (pointers[index] == NULL) {
            size_t size =
                8U + (i * 67U) % 1017U;

            pointers[index] =
                allocate_memory(size);

            if (pointers[index] != NULL) {
                memset(
                    pointers[index],
                    (int)(i & 0xffU),
                    size
                );
            }
        } else {
            release_memory(pointers[index]);
            pointers[index] = NULL;
        }
    }

    remember_stats();

    for (size_t i = 0; i < slots; ++i) {
        release_memory(pointers[i]);
    }

    free(pointers);
}

/* Сценарий 3: крупные блоки памяти. */
static void scenario_large(void)
{
    const size_t count = 96;

    void **pointers =
        calloc(count, sizeof(*pointers));

    if (pointers == NULL) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }

    for (size_t i = 0; i < count; ++i) {
        size_t size =
            (256U + (i % 8U) * 96U)
            * 1024U;

        pointers[i] =
            allocate_memory(size);

        if (pointers[i] != NULL) {
            memset(
                pointers[i],
                (int)(i & 0xffU),
                size
            );
        }
    }

    for (size_t i = 0; i < count; i += 4U) {
        release_memory(pointers[i]);
        pointers[i] = NULL;
    }

    /* Проверяем увеличение блоков через realloc. */
    for (size_t i = 1; i < count; i += 5U) {
        if (pointers[i] != NULL) {
            size_t new_size =
                (768U + (i % 4U) * 128U)
                * 1024U;

            void *resized =
                resize_memory(
                    pointers[i],
                    new_size
                );

            if (resized != NULL) {
                pointers[i] = resized;

                memset(
                    pointers[i],
                    0x3c,
                    new_size
                );
            }
        }
    }

    remember_stats();

    for (size_t i = 0; i < count; ++i) {
        release_memory(pointers[i]);
    }

    free(pointers);
}

static void print_usage(const char *program)
{
    fprintf(
        stderr,
        "Использование: %s "
        "first|best|glibc "
        "small|alternating|large\n",
        program
    );
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    my_fit_strategy strategy =
        MY_FIRST_FIT;

    custom_allocator =
        strcmp(argv[1], "glibc") != 0;

    if (strcmp(argv[1], "first") == 0) {
        strategy = MY_FIRST_FIT;
    } else if (
        strcmp(argv[1], "best") == 0
    ) {
        strategy = MY_BEST_FIT;
    } else if (
        strcmp(argv[1], "glibc") != 0
    ) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    if (custom_allocator) {
        if (my_allocator_init(
                REGION_SIZE,
                strategy
            ) != 0) {
            perror("my_allocator_init");
            return EXIT_FAILURE;
        }
    }

    struct timespec start;
    struct timespec finish;

    clock_gettime(
        CLOCK_MONOTONIC,
        &start
    );

    if (strcmp(argv[2], "small") == 0) {
        scenario_small();
    } else if (
        strcmp(argv[2], "alternating") == 0
    ) {
        scenario_alternating();
    } else if (
        strcmp(argv[2], "large") == 0
    ) {
        scenario_large();
    } else {
        print_usage(argv[0]);

        if (custom_allocator) {
            my_allocator_destroy();
        }

        return EXIT_FAILURE;
    }

    clock_gettime(
        CLOCK_MONOTONIC,
        &finish
    );

    double external_fragmentation = 0.0;

    if (
        custom_allocator &&
        snapshot.total_free != 0
    ) {
        external_fragmentation =
            1.0 -
            (double)snapshot.largest_free /
            (double)snapshot.total_free;
    }

    if (custom_allocator) {
        printf(
            "%s,%s,%.3f,%ld,"
            "%.4f,%zu,%zu\n",
            argv[2],
            argv[1],
            elapsed_ms(start, finish),
            peak_rss_kb(),
            external_fragmentation,
            snapshot.internal_fragmentation,
            failures
        );

        my_allocator_destroy();
    } else {
        printf(
            "%s,%s,%.3f,%ld,"
            "N/A,N/A,%zu\n",
            argv[2],
            argv[1],
            elapsed_ms(start, finish),
            peak_rss_kb(),
            failures
        );
    }

    return failures == 0
        ? EXIT_SUCCESS
        : EXIT_FAILURE;
}

