# Classic LEX & YACC (C) Implementation

This directory contains the university syllabus specification using **Flex (Lex)** and **Bison (Yacc)** in C.

## Files
- `lexer.l`: Lexical analyzer specification matching token regular expressions.
- `parser.y`: LALR(1) Context-Free Grammar productions and syntax validation rules.
- `ast.h` & `ast.c`: C data structures representing the Abstract Syntax Tree.
- `Makefile`: Build instructions using standard `gcc`, `flex`, and `bison`.

## Compilation
On Linux / WSL or MinGW:
```bash
make
./mini_sql
```

Enter any SQL query (e.g., `SELECT name, age FROM students WHERE age >= 18;`) followed by `Ctrl+D` (EOF) to parse.
