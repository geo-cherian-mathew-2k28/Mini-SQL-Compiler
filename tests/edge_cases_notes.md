# Edge-Case Hazards & Compiler Verification Notes

This document accompanies `tests/test_edge_cases.sql` and explains the precise compilation hazards, lookahead considerations, and operator precedence rules tested by each edge case.

---

## Technical Edge-Case Catalog

### 1. `TC-EDGE-01` & `TC-EDGE-02`: Operator Substring Lookahead
- **Compilation Hazard:** Greedy multi-character matching in the Lexer. Operators such as `>=`, `<=`, `<>`, and `!=` share single-character prefixes with `>`, `<`, and `=`.
- **Lookahead Resolution:** The lexer uses a 2-character lookahead window (`peek()` and `advance()`) to ensure `>=` is recognized as a single `GREATER_EQUAL` token rather than `GREATER_THAN` followed by `ASSIGN_EQUAL`.
- **No-Space Stress:** Verifies that expressions like `age>=18` emit exactly three tokens (`IDENTIFIER`, `OPERATOR`, `NUMBER`) without requiring delimiter spaces.

### 2. `TC-EDGE-03`: Whitespace & Newline Invariance
- **Compilation Hazard:** Lexers that improperly track column offsets or fail on multiline SQL input.
- **Resolution:** The lexer skips ASCII spaces, tabs (`\t`), carriage returns (`\r`), and newlines (`\n`) while maintaining accurate 1-based `line` and `column` tracking for subsequent tokens.

### 3. `TC-EDGE-04`: Snake_Case & Numeric Identifier Parsing
- **Compilation Hazard:** Tokenizing identifiers containing internal digits (e.g., `student_id`, `emp_2026`) vs numeric literals.
- **Resolution:** Lexer enforces `[a-zA-Z_][a-zA-Z0-9_]*`. Digits following an alpha or underscore remain attached to the identifier token.

### 4. `TC-EDGE-05`: String Literals with Internal Punctuation
- **Compilation Hazard:** Premature string termination caused by embedded commas, hyphens, or spaces.
- **Resolution:** The string scanner accumulates all characters until it matches the closing delimiter quote `'`.

### 5. `TC-EDGE-06`: Classical Boolean Precedence (`AND` over `OR`)
- **Grammar Level:**
  ```text
  expression  -> and_term ( "OR" and_term )*
  and_term    -> factor ( "AND" factor )*
  ```
- **Hazard:** Naive left-to-right parsers without precedence layering might evaluate `A OR B AND C` as `(A OR B) AND C`.
- **Expected AST:** Resolves strictly as `A OR (B AND C)` according to standard boolean algebra.

### 6. `TC-EDGE-07`: Arbitrary Parenthetical Nesting
- **Compilation Hazard:** Stack overflow or recursion mismatch when parsing nested sub-expressions `((A AND B) OR (C AND D)) AND E`.
- **Resolution:** Mutual recursion between `_parse_or_expr` and `_parse_primary_expr` handles arbitrary parenthetical depths deterministically.

### 7. `TC-EDGE-08`: Mixed Multi-Column Sorting
- **Compilation Hazard:** Parser failing to loop across comma-separated sorting descriptors or defaulting subsequent columns to the previous column's sort direction.
- **Resolution:** `_parse_order_by()` explicitly loops through `OrderByItem` instances, each maintaining its own column token and direction (`ASC`/`DESC`).

### 8. `TC-EDGE-09`: Unary Negation (`NOT`)
- **Compilation Hazard:** Misinterpreting `NOT` as an identifier or failing to associate it with the enclosed sub-expression.
- **Resolution:** `_parse_primary_expr()` checks for `KEYWORD_NOT` and wraps the subsequent condition in a unary expression node.

### 9. `TC-EDGE-10`: Keyword Literals (`TRUE`, `FALSE`, `NULL`)
- **Compilation Hazard:** Treating boolean or null literals as column identifiers.
- **Resolution:** The lexer matches keywords case-insensitively and emits `KEYWORD_TRUE`, `KEYWORD_FALSE`, and `KEYWORD_NULL` tokens, which the parser folds into typed `Literal` AST nodes.

### 10. `TC-EDGE-11` & `TC-EDGE-12`: Optional Syntax Elements
- **Compilation Hazard:** Enforcing rigid optional requirements (e.g., failing if `;` or `ASC` is missing).
- **Resolution:** Semicolons are parsed as optional statement terminators, and omitted sort directions automatically default to `ASC`.
