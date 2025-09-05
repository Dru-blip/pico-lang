CC      := clang
CFLAGS  := -Wall -g -O3 -std=c23 -Iinclude

OUTDIR  := out
PICOC_BIN := $(OUTDIR)/picoc
PICOC_SRCS := compiler/main.c $(wildcard compiler/src/*.c)

all: $(PICOC_BIN)

$(PICOC_BIN):  outdir
	$(CC) $(CFLAGS) -o $@ $(PICOC_SRCS)

compiler: $(PICOC_BIN)

outdir:
	mkdir -p $(OUTDIR)

clean:
	rm -rf $(OUTDIR)
