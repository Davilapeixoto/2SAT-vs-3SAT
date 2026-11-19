CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -Wpedantic

.PHONY: all test clean

all: 2sat 3sat

2sat: algoritmos/c/2sat.c algoritmos/c/cnf.c algoritmos/c/cnf.h
	$(CC) $(CFLAGS) algoritmos/c/2sat.c algoritmos/c/cnf.c -o 2sat

3sat: algoritmos/c/3sat.c algoritmos/c/cnf.c algoritmos/c/cnf.h
	$(CC) $(CFLAGS) algoritmos/c/3sat.c algoritmos/c/cnf.c -o 3sat

clean:
	rm -f 2sat 3sat
