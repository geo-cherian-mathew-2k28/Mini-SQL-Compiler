# Mini SQL Compiler — Viva Voce Examination Guide

This guide compiles high-frequency viva examination questions covering Compiler Design foundational theory, formal language models, parsing strategies, and specific implementation details of the Mini SQL Compiler.

---

## Part 1: Foundational Compiler Theory

### Q1: What constitutes the "front-end" versus the "back-end" of a compiler?
**Answer:**  
The **front-end** is machine-independent and language-dependent. It translates the source program into an Intermediate Representation (IR) while checking correctness. Its phases include:
1. Lexical Analysis (Scanner)
2. Syntax Analysis (Parser)
3. Semantic Analysis (Type checking, Symbol Table validation)

The **back-end** is machine-dependent and language-independent. It takes the IR and transforms it into target code through Intermediate Code Optimization, Target Code Generation (assembly or machine bytecode), and Machine-Dependent Optimization.

---

### Q2: What is the fundamental difference between a Token, a Lexeme, and a Pattern?
**Answer:**
- **Pattern:** The formal rule or regular expression defining the shape of a valid symbol class (e.g., `[a-zA-Z_][a-zA-Z0-9_]*` for identifiers).
- **Lexeme:** The actual sequence of characters in the source text that matches a given pattern (e.g., `students`, `age`, `42`).
- **Token:** An abstract grammatical symbol emitted by the lexer, usually structured as a pair `(Token_Type, Attribute_Value)` (e.g., `<IDENTIFIER, "students">`, `<KEYWORD_SELECT, None>`).

---

### Q3: Why is Lexical Analysis separated from Syntax Analysis?
**Answer:**
1. **Simplicity of Design:** Stripping whitespace, comments, and character-level scanning into a regex-based finite automaton simplifies the Context-Free Grammar used in the parser.
2. **Compiler Efficiency:** Lexers process raw characters using simple state transitions (regular expressions), which run much faster than the pushdown automaton / recursive stack required for parsing.
3. **Portability:** Language character encodings or dialect differences can be isolated in the lexer without altering the parser.

---

### Q4: Why can't Regular Expressions alone parse SQL? Why do we need a Context-Free Grammar (CFG)?
**Answer:**  
Regular expressions and Deterministic Finite Automata (DFAs) have finite memory and cannot recognize languages requiring arbitrary nesting or balanced delimiters (e.g., arbitrarily nested parentheses like `((age > 18 AND gpa > 3.0) OR (credits = 4))` or matching quotes). A Context-Free Grammar, powered by a Pushdown Automaton (with an unbounded stack), is mathematically necessary to recognize hierarchical, recursive syntactic structures.

---

### Q5: What is the difference between a Parse Tree (Concrete Syntax Tree) and an Abstract Syntax Tree (AST)?
**Answer:**
- **Parse Tree (CST):** A concrete, literal pictorial representation of the derivation rules applied according to the CFG. It contains every non-terminal, comma, delimiter, parenthesis, and terminal token, making it verbose.
- **AST:** A condensed, semantic representation of the query. Syntactic clutter (such as commas, semicolons, and parentheses used only for grouping) is discarded. Internal nodes represent operators (e.g., `BinaryExpr(>=)`), and leaf nodes represent operands (e.g., `Identifier(age)`, `Literal(20)`).

---

### Q6: What is Left-Recursion and why must it be eliminated in Top-Down Parsers?
**Answer:**  
Left-recursion occurs when a non-terminal derives a sentential form beginning with itself ($A \to A\alpha$). In top-down parsers (such as recursive descent), invoking a parsing function for $A$ immediately causes it to invoke itself recursively without consuming any input token, resulting in an infinite recursion stack overflow. It is eliminated by converting the rule into a right-recursive or iterative equivalent ($A \to \beta A', A' \to \alpha A' \mid \epsilon$).

---

### Q7: What is Left-Factoring and when is it required?
**Answer:**  
Left-factoring is a grammar transformation used when two or more production alternatives share a common prefix ($A \to \alpha\beta_1 \mid \alpha\beta_2$). A top-down parser cannot decide which production to choose by inspecting only the next lookahead token. Left-factoring extracts the common prefix:
$$A \to \alpha A', \quad A' \to \beta_1 \mid \beta_2$$

---

### Q8: What does it mean for a grammar to be LL(1)?
**Answer:**
- **First L:** Scans the input from **L**eft to right.
- **Second L:** Produces a **L**eftmost derivation.
- **(1):** Uses **1** token of lookahead to make parsing decisions deterministically without backtracking.  
For a grammar to be LL(1), the $\text{FIRST}$ sets of all alternative productions for every non-terminal must be disjoint, and if a production can derive $\epsilon$, its $\text{FIRST}$ set must be disjoint from its $\text{FOLLOW}$ set.

---

## Part 2: Mini SQL Compiler Implementation Specifics

### Q9: How does our parser enforce operator precedence without an external table?
**Answer:**  
Precedence is encoded directly into the grammar hierarchy using **precedence climbing**:
1. `_parse_or_expr()` handles lowest-precedence `OR` operations.
2. `_parse_and_term()` handles medium-precedence `AND` operations.
3. `_parse_primary_expr()` handles highest-precedence operations: relational comparisons (`>=`, `=`, etc.), unary operators (`NOT`), and parenthetical groupings `(...)`.  
Because `_parse_and_term()` is called inside `_parse_or_expr()`, `AND` binds tighter than `OR` automatically.

---

### Q10: How does the Lexer distinguish `>=` from `>`?
**Answer:**  
The lexer maintains a 2-character lookahead window using helper methods `peek()` and `advance()`. When it encounters a `>` character, it inspects the next character without immediately consuming it. If the next character is `=`, it consumes both and emits a single `GREATER_EQUAL` token; otherwise, it emits a `GREATER_THAN` token.

---

### Q11: What semantic checks are performed in our compiler?
**Answer:**
1. **Relation Validation:** Ensures the table specified in the `FROM` clause exists in the schema catalog.
2. **Attribute Validation:** Ensures every column referenced in the `SELECT`, `WHERE`, and `ORDER BY` clauses exists in that specific table.
3. **Projection Consistency:** Rejects queries that erroneously attempt to combine wildcard selection with explicit column names (e.g., `SELECT *, name FROM students`).

---

### Q12: Why did we build a custom hand-written Lexer and Parser instead of relying solely on Flex/Bison?
**Answer:**
1. **First-Principles Understanding:** Hand-crafting the tokenizer and recursive descent functions provides intimate mastery over lookahead buffers, call stacks, and AST node construction.
2. **Portability & Zero Dependencies:** The Python implementation runs out of the box on Windows, macOS, and Linux without requiring C compilers or Unix toolchains.
3. **Dual Compliance:** We also created a parallel C/Lex/Yacc reference implementation in `c_lex_yacc/` (`lexer.l` and `parser.y`) to demonstrate proficiency with traditional UNIX compiler-generation tools.

---

## Part 3: Individual Member Viva Preparation

### For Geo Cherian Mathew (Core Architecture & Parser):
- **Target Question:** *"Walk us through how your parser constructs an AST node for a binary expression."*
- **Answer:** *"In `_parse_primary_expr()`, the parser matches a left operand (an identifier or literal). It then peeks at the next token to check for a relational operator (`=`, `>=`, etc.). If matched, it advances past the operator and recursively calls `_parse_primary_expr()` to retrieve the right operand. It then encapsulates all three components into an immutable `BinaryExpr(op, left, right)` node and returns it up the call stack."*

### For Liya Tomy (Documentation & Governance):
- **Target Question:** *"Why is formal documentation of language boundaries critical in compiler projects?"*
- **Answer:** *"Full SQL is vast. Documenting the exact grammar subset, mandatory clause sequence (`SELECT -> FROM -> WHERE -> ORDER BY`), and explicitly unsupported features prevents scope creep, guides negative test case design, and provides examiners with an honest, verifiable feature checklist."*

### For Elkin Wilson George (SQL Specification & Boundaries):
- **Target Question:** *"What happens if a user submits a query where WHERE precedes FROM?"*
- **Answer:** *"The parser expects the `FROM` token immediately after the projection list. When it encounters `WHERE` instead, it rejects the query as an out-of-order syntax violation, emitting the exact diagnostic: `Expected 'FROM' keyword, but found 'WHERE'` with line and column coordinates."*

### For Joswin Joshy (Lexical Specification & Tokens):
- **Target Question:** *"How does your regular expression for identifiers handle alphanumeric names and keywords?"*
- **Answer:** *"The pattern `[a-zA-Z_][a-zA-Z0-9_]*` matches alphanumeric character streams starting with a letter or underscore. Once scanned, the string is converted to uppercase and checked against a reserved keyword lookup dictionary. If a match exists, a dedicated keyword token is emitted; otherwise, it defaults to a general identifier token."*

### For Jonathan Kuruvilla Thomas (Verification & Test Suite):
- **Target Question:** *"How did you verify that the compiler produces correct ASTs for valid queries?"*
- **Answer:** *"We developed a golden reference test suite (`tests/test_golden_ast.py`) utilizing standardized JSON AST fixtures. Each valid query is compiled and its generated AST is dynamically compared against the golden JSON tree to guarantee structural and semantic fidelity."*

### For Justin Mathew Philip (Diagnostics & Negative Testing):
- **Target Question:** *"Why are negative tests just as important as positive tests in compiler design?"*
- **Answer:** *"A compiler's value is judged as much by its error reporting as its successful compilation. Negative testing verifies that the compiler gracefully rejects malformed inputs, never crashes or produces unhandled exceptions, and provides actionable error messages pinpointing the exact phase, token, line, and column of the mistake."*
