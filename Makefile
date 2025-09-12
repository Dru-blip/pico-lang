CC      := clang
CFLAGS  := -Wall -g -O3 -std=c23 -Iinclude

OUTDIR  := out

PICO_BIN := $(OUTDIR)/pico
PICO_SRCS := $(wildcard runtime/*.c)

all: $(PICO_BIN) compiler

$(PICO_BIN): outdir
	$(CC) $(CFLAGS) -o $@ $(PICO_SRCS) -ldl

compiler: compiler/main.py
	pyinstaller --onefile $< --name picoc

runtime: $(PICO_BIN)

outdir:
	mkdir -p $(OUTDIR)

clean:
	rm -rf $(OUTDIR)

.PHONY : all clean compiler runtime
