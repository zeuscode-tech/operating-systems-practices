#define _GNU_SOURCE

#include "my_alloc.h"

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#define ALIGNMENT 16U
#define BLOCK_MAGIC UINT32_C(0xB10C4A11)

typedef struct Block {
    size_t capacity;
    size_t requested;
    struct Block *next;
    struct Block *previous;
    uint32_t magic;
    int is_free;
} Block;

static void *region_base;
static size_t region_size;
static Block *first_block;
static my_fit_strategy current_strategy = MY_FIRST_FIT;
static size_t current_used;
static size_t peak_used;

static size_t align_up(size_t value)
{
    return (value + ALIGNMENT - 1U) & ~(ALIGNMENT - 1U);
}

static size_t header_size(void)
{
    return align_up(sizeof(Block));
}

static void *block_payload(Block *block)
{
    return (char *)block + header_size();
}

static Block *find_block_by_pointer(void *pointer)
{
    for (Block *block = first_block; block != NULL; block = block->next) {
        if (block->magic == BLOCK_MAGIC &&
            block_payload(block) == pointer) {
            return block;
        }
    }

    return NULL;
}

static Block *find_free_block(size_t capacity)
{
    Block *best = NULL;

    for (Block *block = first_block;
         block != NULL;
         block = block->next) {

        if (!block->is_free || block->capacity < capacity) {
            continue;
        }

        if (current_strategy == MY_FIRST_FIT) {
            return block;
        }

        if (best == NULL || block->capacity < best->capacity) {
            best = block;
        }
    }

    return best;
}

static void merge_with_next(Block *block)
{
    Block *next = block->next;

    if (next == NULL || !next->is_free) {
        return;
    }

    block->capacity += header_size() + next->capacity;
    block->next = next->next;

    if (block->next != NULL) {
        block->next->previous = block;
    }

    next->magic = 0;
}

static void split_block(Block *block, size_t wanted_capacity)
{
    size_t minimum_tail = header_size() + ALIGNMENT;

    if (block->capacity < wanted_capacity + minimum_tail) {
        return;
    }

    Block *tail =
        (Block *)((char *)block_payload(block) + wanted_capacity);

    tail->capacity =
        block->capacity - wanted_capacity - header_size();
    tail->requested = 0;
    tail->next = block->next;
    tail->previous = block;
    tail->magic = BLOCK_MAGIC;
    tail->is_free = 1;

    if (tail->next != NULL) {
        tail->next->previous = tail;
    }

    block->next = tail;
    block->capacity = wanted_capacity;

    if (tail->next != NULL && tail->next->is_free) {
        merge_with_next(tail);
    }
}

int my_allocator_init(
    size_t wanted_region_size,
    my_fit_strategy strategy
)
{
    if (region_base != NULL) {
        errno = EALREADY;
        return -1;
    }

    if (strategy != MY_FIRST_FIT &&
        strategy != MY_BEST_FIT) {
        errno = EINVAL;
        return -1;
    }

    if (wanted_region_size >
        SIZE_MAX - (ALIGNMENT - 1U)) {
        errno = ENOMEM;
        return -1;
    }

    wanted_region_size = align_up(wanted_region_size);

    if (wanted_region_size <
        header_size() + ALIGNMENT) {
        errno = EINVAL;
        return -1;
    }

    void *memory = mmap(
        NULL,
        wanted_region_size,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    if (memory == MAP_FAILED) {
        return -1;
    }

    region_base = memory;
    region_size = wanted_region_size;
    current_strategy = strategy;
    current_used = 0;
    peak_used = 0;

    first_block = (Block *)region_base;
    first_block->capacity =
        region_size - header_size();
    first_block->requested = 0;
    first_block->next = NULL;
    first_block->previous = NULL;
    first_block->magic = BLOCK_MAGIC;
    first_block->is_free = 1;

    return 0;
}

void my_allocator_destroy(void)
{
    if (region_base == NULL) {
        return;
    }

    size_t leaks = 0;

    for (Block *block = first_block;
         block != NULL;
         block = block->next) {

        if (!block->is_free) {
            ++leaks;
        }
    }

    if (leaks != 0) {
        fprintf(
            stderr,
            "my_allocator: обнаружено утечек: %zu\n",
            leaks
        );
    }

    munmap(region_base, region_size);

    region_base = NULL;
    region_size = 0;
    first_block = NULL;
    current_used = 0;
    peak_used = 0;
}

void my_allocator_set_strategy(
    my_fit_strategy strategy
)
{
    if (strategy == MY_FIRST_FIT ||
        strategy == MY_BEST_FIT) {
        current_strategy = strategy;
    }
}

void *my_malloc(size_t size)
{
    if (region_base == NULL || size == 0) {
        return NULL;
    }

    if (size > SIZE_MAX - (ALIGNMENT - 1U)) {
        errno = ENOMEM;
        return NULL;
    }

    size_t capacity = align_up(size);
    Block *block = find_free_block(capacity);

    if (block == NULL) {
        errno = ENOMEM;
        return NULL;
    }

    split_block(block, capacity);

    block->is_free = 0;
    block->requested = size;

    current_used += size;

    if (current_used > peak_used) {
        peak_used = current_used;
    }

    return block_payload(block);
}

void my_free(void *pointer)
{
    if (pointer == NULL) {
        return;
    }

    Block *block = find_block_by_pointer(pointer);

    if (block == NULL) {
        fprintf(
            stderr,
            "my_free: недопустимый указатель\n"
        );
        return;
    }

    if (block->is_free) {
        fprintf(
            stderr,
            "my_free: повторное освобождение блока\n"
        );
        return;
    }

    current_used -= block->requested;
    block->requested = 0;
    block->is_free = 1;

    /* Слияние со следующим свободным блоком. */
    merge_with_next(block);

    /* Слияние с предыдущим свободным блоком. */
    if (block->previous != NULL &&
        block->previous->is_free) {

        block = block->previous;
        merge_with_next(block);
    }
}

void *my_realloc(
    void *pointer,
    size_t new_size
)
{
    if (pointer == NULL) {
        return my_malloc(new_size);
    }

    if (new_size == 0) {
        my_free(pointer);
        return NULL;
    }

    if (new_size >
        SIZE_MAX - (ALIGNMENT - 1U)) {
        errno = ENOMEM;
        return NULL;
    }

    Block *block = find_block_by_pointer(pointer);

    if (block == NULL || block->is_free) {
        fprintf(
            stderr,
            "my_realloc: недопустимый указатель\n"
        );
        return NULL;
    }

    size_t old_size = block->requested;
    size_t wanted_capacity = align_up(new_size);

    /*
     * Новый размер помещается в текущий блок.
     * Лишнюю часть отделяем в свободный блок.
     */
    if (wanted_capacity <= block->capacity) {
        block->requested = new_size;
        current_used =
            current_used - old_size + new_size;

        split_block(block, wanted_capacity);
        return pointer;
    }

    /*
     * Пробуем расширить блок за счёт
     * следующего свободного соседа.
     */
    if (block->next != NULL &&
        block->next->is_free &&
        block->capacity +
            header_size() +
            block->next->capacity
            >= wanted_capacity) {

        merge_with_next(block);
        split_block(block, wanted_capacity);

        block->requested = new_size;
        current_used =
            current_used - old_size + new_size;

        if (current_used > peak_used) {
            peak_used = current_used;
        }

        return pointer;
    }

    /*
     * Расширить на месте нельзя:
     * выделяем новый блок и копируем данные.
     */
    void *new_pointer = my_malloc(new_size);

    if (new_pointer == NULL) {
        return NULL;
    }

    size_t copy_size =
        old_size < new_size ? old_size : new_size;

    memcpy(new_pointer, pointer, copy_size);
    my_free(pointer);

    return new_pointer;
}

my_allocator_stats my_allocator_get_stats(void)
{
    my_allocator_stats stats = {0};
    stats.peak_used = peak_used;

    for (Block *block = first_block;
         block != NULL;
         block = block->next) {

        ++stats.block_count;

        if (block->is_free) {
            stats.total_free += block->capacity;

            if (block->capacity >
                stats.largest_free) {
                stats.largest_free =
                    block->capacity;
            }
        } else {
            stats.used_memory +=
                block->requested;

            stats.internal_fragmentation +=
                block->capacity -
                block->requested;
        }
    }

    return stats;
}

void my_allocator_print(void)
{
    size_t number = 0;

    for (Block *block = first_block;
         block != NULL;
         block = block->next) {

        size_t offset =
            (size_t)((char *)block -
                     (char *)region_base);

        printf(
            "%zu: offset=%zu %s "
            "capacity=%zu requested=%zu\n",
            number++,
            offset,
            block->is_free ? "FREE" : "USED",
            block->capacity,
            block->requested
        );
    }
}
