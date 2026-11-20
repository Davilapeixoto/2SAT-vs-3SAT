CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -Wpedantic
PYTHON = python3

PY_SRCS = algoritmos/python/cnf.py algoritmos/python/2sat.py algoritmos/python/3sat.py

.PHONY: all check-py test benchmark run-2sat-c run-3sat-c run-2sat-py run-3sat-py clean

all: 2sat 3sat check-py

2sat: algoritmos/c/2sat.c algoritmos/c/cnf.c algoritmos/c/cnf.h
	$(CC) $(CFLAGS) algoritmos/c/2sat.c algoritmos/c/cnf.c -o 2sat

3sat: algoritmos/c/3sat.c algoritmos/c/cnf.c algoritmos/c/cnf.h
	$(CC) $(CFLAGS) algoritmos/c/3sat.c algoritmos/c/cnf.c -o 3sat

check-py: $(PY_SRCS)
	$(PYTHON) -m py_compile $(PY_SRCS)

run-2sat-c: 2sat
	./2sat $(or $(FILE),dados/2sat_basico_sat.cnf)

run-3sat-c: 3sat
	./3sat $(or $(FILE),dados/3sat_basico_sat.cnf)

run-2sat-py:
	$(PYTHON) algoritmos/python/2sat.py $(or $(FILE),dados/2sat_basico_sat.cnf)

run-3sat-py:
	$(PYTHON) algoritmos/python/3sat.py $(or $(FILE),dados/3sat_basico_sat.cnf)

test: all
	$(PYTHON) tests/test.py

benchmark: all
	$(PYTHON) scripts/benchmark.py

clean:
	rm -f 2sat 3sat
	rm -rf algoritmos/python/__pycache__ tests/__pycache__ scripts/__pycache__