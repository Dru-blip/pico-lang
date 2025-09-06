CC      := clang
CFLAGS  := -Wall -g -O3 -std=c23 -Iinclude

OUTDIR  := out

PICOC_BIN := $(OUTDIR)/picoc
PICOC_SRCS := $(wildcard compiler/*.c)

PICO_BIN := $(OUTDIR)/pico
PICO_SRCS := $(wildcard runtime/*.c)

all: $(PICOC_BIN) $(PICO_BIN)

$(PICOC_BIN):  outdir
	$(CC) $(CFLAGS) -o $@ $(PICOC_SRCS)

$(PICO_BIN): outdir
	$(CC) $(CFLAGS) -o $@ $(PICO_SRCS)

compiler: $(PICOC_BIN)

outdir:
	mkdir -p $(OUTDIR)

clean:
	rm -rf $(OUTDIR)
