# Golden AST Reference Suite

This directory contains the golden master AST JSON fixtures used for automated regression testing of the Mini SQL Compiler.

## Fixtures Catalog
1. `simple_select.json`: `SELECT id, name FROM users;`
2. `wildcard_select.json`: `SELECT * FROM customers;`
3. `where_simple.json`: `SELECT id FROM orders WHERE amount > 100;`
4. `where_compound.json`: `SELECT id FROM logs WHERE level = 'ERROR' AND code = 500;`
5. `full_query.json`: `SELECT name, score FROM students WHERE score >= 50 ORDER BY score DESC;`

## Automated Verification
Executed automatically via `tests/test_golden_ast.py`.
