CC = gcc
CFLAGS = -Wall -Wextra -g

all: mini_sql

mini_sql: lex.yy.c parser.tab.c ast.c
	$(CC) $(CFLAGS) lex.yy.c parser.tab.c ast.c -o mini_sql

lex.yy.c: lexer.l parser.tab.h
	flex lexer.l

parser.tab.c parser.tab.h: parser.y
	bison -d parser.y

clean:
	rm -f lex.yy.c parser.tab.c parser.tab.h mini_sql
