#if defined(__linux__)
#define _POSIX_C_SOURCE 200809L
#endif

/* ПР-11, уровень C. Реальные страничные отказы и обход по строкам/столбцам.
 * Сборка: gcc -Wall -Wextra -O2 -o faults faults.c
 * Запуск: ./faults [N]   (матрица N x N значений int, по умолчанию 4096)
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <time.h>

static void usage_now(long *minor, long *major)
{
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    *minor = ru.ru_minflt;
    *major = ru.ru_majflt;
}

static double seconds_now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main(int argc, char *argv[])
{
    size_t n = (argc > 1) ? (size_t)atol(argv[1]) : 4096;
    long mi0, ma0, mi1, ma1;

    usage_now(&mi0, &ma0);
    int *m = malloc(n * n * sizeof(int));
    if (m == NULL) {
        perror("malloc");
        return 1;
    }
    usage_now(&mi1, &ma1);
    printf("malloc %zu MiB: minor=%ld major=%ld\n",
           n * n * sizeof(int) >> 20, mi1 - mi0, ma1 - ma0);

    usage_now(&mi0, &ma0);
    for (size_t i = 0; i < n * n; i++)
        m[i] = (int)i;
    usage_now(&mi1, &ma1);
    printf("first touch:      minor=%ld major=%ld\n", mi1 - mi0, ma1 - ma0);

    long long sum = 0;
    double t0 = seconds_now();
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < n; j++)
            sum += m[i * n + j];
    double t_rows = seconds_now() - t0;

    t0 = seconds_now();
    for (size_t j = 0; j < n; j++)
        for (size_t i = 0; i < n; i++)
            sum += m[i * n + j];
    double t_cols = seconds_now() - t0;

    printf("by rows:    %.3f s\n", t_rows);
    printf("by columns: %.3f s  (x%.1f)\n", t_cols, t_cols / t_rows);
    printf("checksum: %lld\n", sum);
    free(m);
    return 0;
}
