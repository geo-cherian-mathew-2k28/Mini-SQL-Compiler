# Academic Project Report: Front-End Compiler for Restricted SQL

**Degree:** Bachelor of Technology in Computer Science and Engineering  
**Subject:** CS304 — Compiler Design Mini-Project  
**Evaluation Date:** 23 October 2026  

---

## Abstract
This project presents the comprehensive design, formal mathematical specification, and software implementation of a modular **Compiler Front-End for a Restricted Subset of Structured Query Language (SQL)**. The compiler recognizes declarative relational statements containing `SELECT`, `FROM`, optional `WHERE`, and optional `ORDER BY` clauses. 

Developed strictly from first principles using pure Python (with zero external runtime dependencies) and accompanied by a parallel C/Flex/Bison implementation, the system executes three core compiler phases: (1) Lexical Analysis using 2-character lookahead regular expression scanning, (2) Syntax Analysis via an LL(1) deterministic recursive descent parser constructing an Abstract Syntax Tree (AST), and (3) Semantic Analysis performing catalog-driven relation and attribute resolution. The project includes an interactive terminal shell (CLI REPL) and a modern Web Studio IDE rendering visual orthogonal flowchart ASTs.

---

## Chapter 1: Introduction & Problem Statement

### 1.1 Context & Motivation
Structured Query Language (SQL) is the standard declarative query language for relational database systems. In commercial relational database management systems (RDBMS) such as PostgreSQL or SQLite, query execution begins with a specialized compiler front-end that scans, parses, and validates the textual query before passing an optimized relational algebra plan to the execution engine.

In standard academic curricula, compiler design coursework frequently focuses on traditional imperative languages (like subsets of C). Applying compiler theory to declarative domain-specific languages (DSLs) like SQL offers students deep insight into syntax-directed translation, operator precedence hierarchies without explicit assignment, and catalog-driven semantic analysis.

### 1.2 Problem Statement
> *"Develop a compiler front end that recognizes a restricted subset of SQL, including `SELECT`, `FROM`, `WHERE`, and `ORDER BY`. Validate query syntax and construct a parse tree (and Abstract Syntax Tree)."*

### 1.3 Scope and Language Boundaries
The compiler restricts ANSI SQL to its fundamental relational query operations:
- **Mandatory Clause Sequence:** $\text{SELECT} \to \text{FROM} \to [\text{WHERE}] \to [\text{ORDER BY}] \to [;]$
- **Supported Features:** Wildcard (`*`) and comma-separated column projections, single table references, binary comparison operators (`=`, `!=`, `<`, `>`, `<=`, `>=`), string/numeric/boolean/null literals, boolean connectives (`AND`, `OR`, `NOT`) with parenthetical nesting, and single/multi-column sorting (`ASC`, `DESC`).
- **Explicit Exclusions:** Multi-table `JOIN` operations, aggregations (`GROUP BY`, `HAVING`), nested subqueries, and Data Modification/Definition statements (`INSERT`, `UPDATE`, `DELETE`, `CREATE`).

---

## Chapter 2: Theoretical Foundations & Grammar Engineering

### 2.1 Context-Free Grammar (CFG) in Backus-Naur Form (BNF)
The initial grammar for the restricted SQL subset was formalized as:

$$\begin{aligned}
\langle Query \rangle &\to \text{SELECT} \;\; \langle Projections \rangle \;\; \text{FROM} \;\; \text{IDENTIFIER} \;\; [\langle WhereClause \rangle] \;\; [\langle OrderByClause \rangle] \;\; [;] \\
\langle Projections \rangle &\to * \;\mid\; \langle IdentList \rangle \\
\langle IdentList \rangle &\to \text{IDENTIFIER} \;\; ( , \;\; \text{IDENTIFIER} )^* \\
\langle WhereClause \rangle &\to \text{WHERE} \;\; \langle OrExpr \rangle \\
\langle OrExpr \rangle &\to \langle AndTerm \rangle \;\; ( \text{OR} \;\; \langle AndTerm \rangle )^* \\
\langle AndTerm \rangle &\to \langle Factor \rangle \;\; ( \text{AND} \;\; \langle Factor \rangle )^* \\
\langle Factor \rangle &\to [\text{NOT}] \;\; \langle Primary \rangle \\
\langle Primary \rangle &\to \langle Predicate \rangle \;\mid\; ( \;\; \langle OrExpr \rangle \;\; ) \\
\langle Predicate \rangle &\to \text{IDENTIFIER} \;\; \langle RelOp \rangle \;\; \langle LiteralOrIdent \rangle \\
\langle OrderByClause \rangle &\to \text{ORDER} \;\; \text{BY} \;\; \langle OrderList \rangle \\
\langle OrderList \rangle &\to \langle OrderItem \rangle \;\; ( , \;\; \langle OrderItem \rangle )^* \\
\langle OrderItem \rangle &\to \text{IDENTIFIER} \;\; [\text{ASC} \mid \text{DESC}]
\end{aligned}$$

### 2.2 Grammar Transformations
Top-down recursive descent parsing requires deterministic, non-left-recursive productions.
1. **Left-Recursion Elimination:** Recursive rules of the form $E \to E + T$ are transformed into iterative loops or right-recursive rules $E \to T E'$, preventing infinite stack recursion.
2. **Left-Factoring:** Common prefixes across production alternatives (e.g., in projections or optional sort directions) are factored to ensure the parser can choose the correct branch using a single lookahead token ($k = 1$).
3. **LL(1) Predictability:** Calculation of $\text{FIRST}$ and $\text{FOLLOW}$ sets proves pairwise disjointness across all branching decisions.

---

## Chapter 3: Lexical Analysis Architecture

The Lexical Analyzer (`src/lexer/lexer.py`) transforms a raw stream of characters into a structured token stream.

### 3.1 Token Model
Each emitted token encapsulates:
- `type`: Categorical token enum (`KEYWORD_SELECT`, `IDENTIFIER`, `OPERATOR`, `NUMBER`, etc.).
- `lexeme`: Exact character slice from the source query.
- `line` & `column`: 1-based source coordinates for diagnostic tracking.

### 3.2 Two-Character Lookahead Scanning
To distinguish compound operators sharing single-character prefixes (e.g., `>=` vs `>`, `<>` vs `<`, `!=` vs `!`), the scanner maintains a lookahead buffer (`peek()` and `advance()`), ensuring greedy matching without ambiguous backtracking.

---

## Chapter 4: Syntax Analysis & AST Construction

The Syntax Analyzer (`src/parser/parser.py`) verifies that the token sequence conforms to the language grammar and synthesizes an Abstract Syntax Tree (AST).

### 4.1 Recursive Descent Architecture
Each major grammatical construct is parsed by a dedicated function:
- `_parse_select_query()`: Entry point validating clause sequencing.
- `_parse_projections()`: Extracts wildcard or attribute sequences.
- `_parse_from_clause()`: Captures and validates source table tokens.
- `_parse_where_clause()`: Implements precedence climbing across boolean operators.
- `_parse_order_by()`: Constructs sorting descriptor lists.

### 4.2 AST Node Hierarchy
Unlike concrete parse trees that retain syntactic trivia (commas, semicolons, keywords), our AST represents the semantic core of the query:
- `SelectQuery`: Root node aggregating clauses.
- `Identifier` & `Table`: Relational operands.
- `BinaryExpr` & `UnaryExpr`: Predicate expression trees.
- `Literal`: Typed constant nodes (`INTEGER`, `FLOAT`, `STRING`, `BOOLEAN`, `NULL`).
- `OrderByItem`: Attribute and direction pair.

---

## Chapter 5: Semantic Analysis & Catalog Validation

The Semantic Analyzer (`src/semantic/analyzer.py`) evaluates the AST against a predefined in-memory database catalog schema (`src/semantic/schema.py`).

### 5.1 Validation Protocol
1. **Table Resolution:** Confirms that the target table identifier exists in the catalog.
2. **Column Scope Resolution:** Traverses projections, `WHERE` condition trees, and `ORDER BY` items to verify that all referenced columns exist within the target table.
3. **Projection Semantic Rules:** Rejects invalid combinations, such as attempting to mix wildcard selection with explicit column names (`SELECT *, age FROM students`).

---

## Chapter 6: User Interfaces & Visualizations

To facilitate practical demonstration and laboratory assessment, two user interfaces were engineered:
1. **Interactive CLI REPL (`src/cli.py`):** An interactive terminal shell featuring multi-line SQL input, schema inspection commands (`.tables`, `.schema`), team credits, and detailed pipeline stage breakdowns.
2. **Web Studio IDE (`src/ui/server.py` & `web/`):** A zero-dependency web interface that renders the AST as an **orthogonal arrow flowchart tree** with color-coded nodes (dark blue clauses, red tables, blue columns, and green literals) along with a Light/Dark theme toggle.

---

## Chapter 7: Verification, Testing & Empirical Results

Systematic verification was conducted across three distinct test dimensions:
1. **Automated Unit Tests:** 46 automated unit tests covering the lexer, parser, semantic analyzer, and golden reference AST fixtures (`python -m unittest discover tests`).
2. **Negative Test Suite (`tests/test_invalid.sql`):** 22 structured invalid queries verifying graceful rejection, positional pinpointing, and categorical diagnostics across Lexical, Syntax, and Semantic errors.
3. **Edge-Case Suite (`tests/test_edge_cases.sql`):** 12 boundary-condition queries testing dense operator lookahead (no spaces), deep parenthetical nesting, and multiline formatting.
4. **Master Test Matrix (`docs/tests/test_matrix.md`):** Complete QA traceability matrix detailing 45 distinct test executions with 100% pass rates.

---

## Chapter 8: Conclusion & Future Scope

The **Mini SQL Compiler** successfully demonstrates the complete front-end lifecycle of a domain-specific compiler from formal CFG specification to visual AST generation and semantic symbol verification. 

### Future Work:
1. Extending the grammar to support relational `JOIN` operations across multiple tables.
2. Intermediate Representation (IR) generation to emit relational algebra execution plans.
3. Integrating a lightweight B-Tree storage engine backend to execute queries against physical files.

---

## References
1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley.
2. Cooper, K. D., & Torczon, L. (2011). *Engineering a Compiler* (2nd ed.). Morgan Kaufmann.
3. Date, C. J. (2004). *An Introduction to Database Systems* (8th ed.). Addison-Wesley.
4. ISO/IEC 9075:2016. *Information technology — Database languages — SQL*.
