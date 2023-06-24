PROG := p2u
SRC := p2u.c
CC := cc
CFLAGS += -g -std=c99 -Wall
LDFLAGS += -lm
PREFIX ?= /usr/local

UNAME := $(shell sh -c 'uname -s 2>/dev/null')

ifeq ($(UNAME), Darwin)
	CC := clang
	CFLAGS += -Wunused-result -Wunused-value
endif

default:
	$(CC) $(CFLAGS) $(SRC) $(LDFLAGS) -o $(PROG)

.PHONY: install clean

install:
	cp $(PROG) $(PREFIX)/bin/$(PROG)

clean:
	rm -rf $(PROG) $(PROG).dSYM

