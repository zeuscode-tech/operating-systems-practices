#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
#ifndef O_DIRECT
    puts("O_DIRECT недоступен на этой системе");
    return EXIT_SUCCESS;
#else
    const size_t alignment = 4096;
    void *buffer = NULL;
    if (posix_memalign(&buffer, alignment, alignment) != 0) {
        perror("posix_memalign");
        return EXIT_FAILURE;
    }
    memset(buffer, 'A', alignment);
    int fd = open("direct-io.bin", O_WRONLY | O_CREAT | O_TRUNC | O_DIRECT, 0600);
    if (fd < 0) { perror("open O_DIRECT"); free(buffer); return EXIT_FAILURE; }
    ssize_t written = write(fd, buffer, alignment);
    if (written < 0) { perror("write O_DIRECT"); close(fd); free(buffer); return EXIT_FAILURE; }
    printf("O_DIRECT: записано %zd байт выровненным буфером\n", written);
    close(fd);
    unlink("direct-io.bin");
    free(buffer);
    return EXIT_SUCCESS;
#endif
}
