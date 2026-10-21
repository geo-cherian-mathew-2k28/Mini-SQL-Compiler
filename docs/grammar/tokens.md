# Lexical Token Specifications & Regular Expression Catalog

**Project:** Mini SQL Compiler  
**Course:** 3rd Year CSE — Compiler Design Mini-Project  
**Phase:** Stage 1 — Lexical Analysis (Scanning)  
**Document Version:** 1.0.0  

---

## 1. Overview of Lexical Analysis

The **Lexical Analyzer (Scanner)** is the first phase of the Mini SQL Compiler front-end. Its primary function is to transform a linear stream of source characters into a discrete sequence of **Tokens** while:
1. Stripping insignificant whitespace (`' '`, `\t`, `\r`, `\n`).
2. Recording 1-based `line` and `column` coordinates for diagnostic tracking.
3. Rejecting unmapped characters (e.g., `@`, `#`, `$`) with explicit `LexicalError` diagnostics.
4. Distinguishing multi-character compound operators (`>=`, `<=`, `<>`, `!=`) from single-character prefixes using a 2-character lookahead window (`peek()` and `advance()`).

---

## 2. Formal Token Specifications Table

The table below catalogs every token category recognized by the compiler front end:

| Token Name | Category | Regular Expression / Pattern | Sample Lexemes | Semantic Attribute (`value`) |
| :--- | :--- | :--- | :--- | :--- |
| **`SELECT`** | Reserved Keyword | `[sS][eE][lL][eE][cC][tT]` | `SELECT`, `select` | None |
| **`FROM`** | Reserved Keyword | `[fF][rR][oO][mM]` | `FROM`, `From` | None |
| **`WHERE`** | Reserved Keyword | `[wW][hH][eE][rR][eE]` | `WHERE`, `where` | None |
| **`ORDER`** | Reserved Keyword | `[oO][rR][dD][eE][rR]` | `ORDER`, `order` | None |
| **`BY`** | Reserved Keyword | `[bB][yY]` | `BY`, `by` | None |
| **`ASC`** | Reserved Keyword | `[aA][sS][cC]` | `ASC`, `asc` | `"ASC"` |
| **`DESC`** | Reserved Keyword | `[dD][eE][sS][cC]` | `DESC`, `desc` | `"DESC"` |
| **`AND`** | Logical Conjunction | `[aA][nN][dD]` | `AND`, `and` | `"AND"` |
| **`OR`** | Logical Disjunction | `[oO][rR]` | `OR`, `or` | `"OR"` |
| **`NOT`** | Logical Negation | `[nN][oO][tT]` | `NOT`, `not` | `"NOT"` |
| **`IDENTIFIER`** | Column / Table Name | `[a-zA-Z_][a-zA-Z0-9_]*` | `name`, `age`, `student_id` | String (`"name"`) |
| **`INT_LITERAL`** | Numeric Literal | `[0-9]+` | `18`, `2026`, `0` | Integer (`18`) |
| **`FLOAT_LITERAL`** | Numeric Literal | `[0-9]+\.[0-9]+` | `3.75`, `0.05` | Float (`3.75`) |
| **`STRING_LITERAL`**| Character Literal | `'[^']*'` | `'John'`, `'Computer Science'` | String (`"John"`) |
| **`EQUALS`** | Relational Operator | `=` | `=` | `"="` |
| **`NOT_EQUALS`** | Relational Operator | `!=` or `<>` | `!=`, `<>` | `"!="` |
| **`LESS_THAN`** | Relational Operator | `<` | `<` | `"<"` |
| **`LESS_EQUALS`**| Relational Operator | `<=` | `<=` | `"<="` |
| **`GREATER_THAN`**| Relational Operator | `>` | `>` | `">"` |
| **`GREATER_EQUALS`**| Relational Operator | `>=` | `>=` | `">="` |
| **`COMMA`** | Punctuation | `,` | `,` | None |
| **`ASTERISK`** | Projection Wildcard | `*` | `*` | `"*"` |
| **`SEMICOLON`** | Terminator | `;` | `;` | None |
| **`LPAREN`** | Delimiter | `\(` | `(` | None |
| **`RPAREN`** | Delimiter | `\)` | `)` | None |
| **`EOF`** | Sentinel | End of Input Stream | `""` | None |

---

## 3. Disambiguation & Scanning Rules

### 3.1 Case-Insensitivity
Keywords in SQL are case-insensitive by design. The scanner matches words using `[a-zA-Z_][a-zA-Z0-9_]*` and normalizes the string to uppercase (`lexeme.upper()`) before consulting the reserved keyword dictionary:
```python
KEYWORDS = {
    "SELECT": TokenType.SELECT,
    "FROM": TokenType.FROM,
    "WHERE": TokenType.WHERE,
    "ORDER": TokenType.ORDER,
    "BY": TokenType.BY,
    "ASC": TokenType.ASC,
    "DESC": TokenType.DESC,
    "AND": TokenType.AND,
    "OR": TokenType.OR,
    "NOT": TokenType.NOT,
}
```
If present in the dictionary, a dedicated keyword token is emitted; otherwise, the token is classified as an `IDENTIFIER`.

### 3.2 Greedy Multi-Character Operator Matching (Lookahead)
When encountering character `>`, `<`, `!`, or `=`, the lexer peeks at the subsequent character to disambiguate:
- `>` followed by `=` $\longrightarrow$ `GREATER_EQUALS` (`>=`)
- `<` followed by `=` $\longrightarrow$ `LESS_EQUALS` (`<=`)
- `<` followed by `>` $\longrightarrow$ `NOT_EQUALS` (`<>`)
- `!` followed by `=` $\longrightarrow$ `NOT_EQUALS` (`!=`)
- Isolated `>` $\longrightarrow$ `GREATER_THAN` (`>`)
- Isolated `<` $\longrightarrow$ `LESS_THAN` (`<`)
- Isolated `=` $\longrightarrow$ `EQUALS` (`=`)

This prevents naive single-character consumption that would erroneously tokenize `>=` as `GREATER_THAN` followed by `EQUALS`.

### 3.3 String Delimiter Handling
Strings are initiated and terminated with single quotation marks (`'`). Any character between the opening quote and the matching closing quote is consumed verbatim, preserving spaces and internal punctuation.

---

## 4. Lexical Error Categories & Diagnostic Behavior

The lexer never crashes or raises unhandled runtime exceptions. Instead, it captures exact error coordinates and raises a structured `LexicalError`:

| Error Condition | Trigger Input | Emitted Diagnostic Message |
| :--- | :--- | :--- |
| **Illegal Character** | `@`, `#`, `$` | `Lexical Error at line L, column C: Unexpected character '@'` |
| **Unterminated String** | `'Alice` | `Lexical Error at line L, column C: Unterminated string literal` |
| **Standalone Exclamation**| `!` not followed by `=` | `Lexical Error at line L, column C: Unexpected character '!'` |

Every error reports 1-based `line` and `column` numbers, allowing both CLI and Web Studio to highlight the exact position of the mistake.
