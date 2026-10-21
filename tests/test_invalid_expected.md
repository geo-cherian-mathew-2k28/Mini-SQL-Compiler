# Expected Diagnostics for Invalid SQL Test Suite

This document defines the formal diagnostic mapping for the negative test cases cataloged in `tests/test_invalid.sql`. Each entry maps the test identifier to its failure category, failing lexeme/token, and expected compiler front-end diagnostic.

---

## Diagnostic Matrix

| Test ID | Category | Failing Token / Input | Expected Diagnostic Message / Behavior |
| :--- | :--- | :--- | :--- |
| **TC-INV-01** | Syntax Error | `name` | `Expected 'SELECT' (statement initiation), but found 'id'` |
| **TC-INV-02** | Syntax Error | `students` | `Expected 'FROM' keyword, but found 'id'` |
| **TC-INV-03** | Syntax Error | `;` / `EOF` | `Expected table identifier after 'FROM', but found ';'` |
| **TC-INV-04** | Syntax Error | `FROM` | `Trailing comma in SELECT clause; expected identifier, but found 'FROM'` |
| **TC-INV-05** | Syntax Error | `,` | `Expected identifier after comma in SELECT clause, but found ','` |
| **TC-INV-06** | Syntax Error | `FROM` | `Expected column list or '*' after 'SELECT', but found 'FROM'` |
| **TC-INV-07** | Syntax Error | `WHERE` | `Expected 'FROM' keyword, but found 'WHERE'` (Clause order violation) |
| **TC-INV-08** | Syntax Error | `WHERE` | `Unexpected token 'WHERE' after ORDER BY clause` (Clause order violation) |
| **TC-INV-09** | Syntax Error | `SELECT` | `Unexpected trailing token 'SELECT'` (Multiple statements disallowed) |
| **TC-INV-10** | Syntax Error | `;` / `EOF` | `Expected literal, column identifier, or '(' in expression, but found ';'` |
| **TC-INV-11** | Syntax Error | `;` / `EOF` | `Expected boolean condition expression after 'WHERE', but found ';'` |
| **TC-INV-12** | Syntax Error | `;` / `EOF` | `Expected expression following logical operator 'AND', but found ';'` |
| **TC-INV-13** | Syntax Error | `)` | `Unexpected token ')' at end of WHERE condition` |
| **TC-INV-14** | Syntax Error | `;` / `EOF` | `Expected matching ')' to close condition expression, but found ';'` |
| **TC-INV-15** | Syntax Error | `;` / `EOF` | `Expected column identifier after 'ORDER BY', but found ';'` |
| **TC-INV-16** | Syntax Error | `SIDEWAYS` | `Expected sort direction ('ASC' or 'DESC') or comma, but found 'id'` |
| **TC-INV-17** | Lexical Error | `@` | `Lexical Error: Unexpected character '@'` with exact line/column |
| **TC-INV-18** | Lexical Error | `'John;` | `Lexical Error: Unterminated string literal` |
| **TC-INV-19** | Lexical Error | `#` | `Lexical Error: Unexpected character '#'` with exact line/column |
| **TC-INV-20** | Semantic Error | `non_existent_table`| `Semantic Error: Table 'non_existent_table' does not exist in schema catalog` |
| **TC-INV-21** | Semantic Error | `non_existent_col`  | `Semantic Error: Column 'non_existent_col' does not exist in table 'students'` |
| **TC-INV-22** | Semantic Error | `*` with `name`   | `Semantic Error: Wildcard projection '*' cannot be combined with explicit column identifiers` |

---

## Compiler Diagnostic Principles
1. **Graceful Termination:** The compiler never raises an unhandled Python exception, segmentation fault, or stack trace on malformed inputs.
2. **Positional Context:** Every diagnostic emitted by the Lexer and Parser reports 1-based `line` and `column` numbers for instant debugging.
3. **Clean Classification:** Every error is unambiguously stamped with its pipeline stage: `[Lexical Analysis]`, `[Syntax Analysis]`, or `[Semantic Analysis]`.
