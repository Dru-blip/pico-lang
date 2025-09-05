CC      := clang
CFLAGS  := -Wall -g -O3 -std=c23 -Iinclude

SRC     := main.c src/stb_ds.c src/token.c src/tokenizer.c

BINDIR  := out
TARGET  := $(BINDIR)/picoc

all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(BINDIR)
	$(CC) $(CFLAGS) -o $@ $(SRC)

clean:
	rm -rf out
