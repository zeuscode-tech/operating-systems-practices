CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -Werror -pedantic

TARGET = benchmark
OBJECTS = my_alloc.o benchmark.o

.PHONY: all clean check results valgrind

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(OBJECTS) -o $(TARGET)

my_alloc.o: my_alloc.c my_alloc.h
	$(CC) $(CFLAGS) -c my_alloc.c -o my_alloc.o

benchmark.o: benchmark.c my_alloc.h
	$(CC) $(CFLAGS) -c benchmark.c -o benchmark.o

check: $(TARGET)
	./benchmark first small
	./benchmark best alternating
	./benchmark glibc large

results: $(TARGET)
	@{ \
		echo "scenario,allocator,time_ms,peak_rss_kb,external_fragmentation,internal_fragmentation,failures"; \
		for scenario in small alternating large; do \
			for allocator in first best glibc; do \
				./$(TARGET) $$allocator $$scenario; \
			done; \
		done; \
	} | tee benchmark_results.csv

valgrind: $(TARGET)
	valgrind --tool=memcheck \
		--leak-check=full \
		--show-leak-kinds=all \
		--track-origins=yes \
		--error-exitcode=1 \
		./benchmark first large

clean:
	rm -f $(OBJECTS) $(TARGET) benchmark_results.csv
