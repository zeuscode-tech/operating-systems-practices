#ifndef MY_ALLOC_H
#define MY_ALLOC_H

#include <stddef.h>

typedef enum {
    MY_FIRST_FIT,
    MY_BEST_FIT
} my_fit_strategy;

typedef struct {
    size_t total_free;
    size_t largest_free;
    size_t used_memory;
    size_t peak_used;
    size_t internal_fragmentation;
    size_t block_count;
} my_allocator_stats;

int my_allocator_init(size_t region_size, my_fit_strategy strategy);
void my_allocator_destroy(void);

void my_allocator_set_strategy(my_fit_strategy strategy);

void *my_malloc(size_t size);
void my_free(void *pointer);
void *my_realloc(void *pointer, size_t new_size);

my_allocator_stats my_allocator_get_stats(void);
void my_allocator_print(void);

#endif
