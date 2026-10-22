# Mini SQL Compiler — Academic Presentation Slides Outline

**Course:** 3rd Year Computer Science and Engineering (Compiler Design Mini-Project)  
**Project Topic:** Front-End Compiler for Restricted SQL (SELECT, FROM, WHERE, ORDER BY)  
**Evaluation Date:** 23 October 2026  
**Team Members:**
1. Geo Cherian Mathew
2. Liya Tomy
3. Elkin Wilson George
4. Joswin Joshy
5. Jonathan Kuruvilla Thomas
6. Justin Mathew Philip

---

## Slide 1: Title & Team Credentials
- **Slide Title:** Modular Front-End Compiler for Restricted SQL
- **Sub-header:** Lexical Tokenization, Deterministic Recursive Descent Parsing, AST Generation, and Catalog-Driven Semantic Analysis
- **Affiliation:** Department of Computer Science & Engineering
- **Team Members & Core Contribution Areas:**
  - *Geo Cherian Mathew:* Compiler Design, Grammar Architecture, Recursive Descent Engine, AST Synthesis
  - *Liya Tomy:* Project Documentation, System Objectives, and Git Governance
  - *Elkin Wilson George:* SQL Language Boundaries & Report Structure (Chapters 1–3)
  - *Joswin Joshy:* Token Specifications, Regex Architecture & Report Structure (Chapters 4–6)
  - *Jonathan Kuruvilla Thomas:* SQL Test Suite & Slide Architecture
  - *Justin Mathew Philip:* Diagnostic Test Suites, Negative Test Matrix & Viva Guide

---

## Slide 2: Problem Statement & Motivation
- **The Challenge:** Full ANSI SQL is an expansive declarative language with complex dynamic execution. Implementing a complete database engine from scratch exceeds the time and scope of a core compiler design lab.
- **The Solution:** Isolate and rigorously construct the **Front-End Pipeline** of a compiler for the core four-clause query subset (`SELECT`, `FROM`, `WHERE`, `ORDER BY`).
- **Core Educational Objective:** Demonstrate pure compiler construction theory—CFG specification, ambiguity resolution, left-recursion elimination, LL(1) parse table criteria, and semantic symbol table validation.

---

## Slide 3: Language Scope & Syntax Boundaries
- **Mandatory Clause Ordering:**
  $$\text{SELECT} \longrightarrow \text{FROM} \longrightarrow [\text{WHERE}] \longrightarrow [\text{ORDER BY}] \longrightarrow [;]$$
- **Supported Grammar Constructs:**
  - Attribute projection: Wildcard (`*`) or comma-separated column identifiers.
  - Source relation: Single table identifier checked against catalog.
  - Predicate logic: Relational operators (`=`, `!=`, `<`, `>`, `<=`, `>=`), Boolean connectives (`AND`, `OR`, `NOT`), nested parenthetical expressions.
  - Literal types: `INTEGER`, `FLOAT`, `STRING`, `BOOLEAN`, `NULL`.
  - Sorting: Single and multi-column ordering with `ASC` / `DESC` directions.
- **Explicit Exclusions:** `JOIN`, `GROUP BY`, `HAVING`, subqueries, DDL (`CREATE`), and DML (`INSERT`, `UPDATE`, `DELETE`).

---

## Slide 4: Compiler Front-End Architecture
- **Pipeline Architecture Diagram:**
  ```text
  Raw SQL Query
       │
       ▼
  [ Stage 1: Lexical Analyzer ]      ──> Token Stream (Type, Lexeme, Line, Col)
       │
       ▼
  [ Stage 2: Recursive Descent Parser ]──> Abstract Syntax Tree (AST Nodes)
       │
       ▼
  [ Stage 3: Semantic Analyzer ]     ──> Schema Catalog Validation & Symbol Resolution
       │
       ▼
  [ Output & Visualization ]        ──> CLI REPL & Web Studio Flowchart
  ```
- **Zero External Dependencies:** Built with pure Python standard library for 100% portability, alongside a parallel C/Lex/Yacc reference implementation.

---

## Slide 5: Lexical Analysis (Scanning Phase)
- **Mechanics:** 2-character lookahead window (`peek()` / `advance()`) to differentiate single vs. multi-character operators (`>` vs `>=`).
- **Token Classification:**
  - Keywords: `SELECT`, `FROM`, `WHERE`, `ORDER`, `BY`, `ASC`, `DESC`, `AND`, `OR`, `NOT`, `TRUE`, `FALSE`, `NULL`.
  - Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`.
  - Literals: Numeric (integer & floating-point) and single-quoted strings.
  - Delimiters: Commas, parentheses, semicolons.
- **Diagnostic Precision:** Immediate lexical error emission with 1-based line and column coordinates on illegal characters (e.g., `@`, `#`) and unterminated strings.

---

## Slide 6: Syntax Analysis & Recursive Descent Parsing
- **Formal Grammar:** Non-left-recursive, left-factored LL(1) Context-Free Grammar.
- **Top-Down Parsing Strategy:** Dedicated parsing functions for each non-terminal:
  - `_parse_select_query()`
  - `_parse_projections()`
  - `_parse_from_clause()`
  - `_parse_where_clause()` -> Precedence climbing through `_parse_or_expr()`, `_parse_and_term()`, and `_parse_primary_expr()`.
  - `_parse_order_by()`
- **Operator Precedence Guarantee:** Enforces that `AND` binds tighter than `OR`, and comparison operators bind tighter than boolean connectives.

---

## Slide 7: AST Synthesis & Semantic Validation
- **Abstract Syntax Tree (AST):** Eliminates syntactic boilerplate (commas, semicolons, keywords) into a lean semantic tree composed of:
  - `SelectQuery` (Root)
  - `Identifier`, `Table`, `BinaryExpr`, `UnaryExpr`, `Literal`, `OrderByItem`.
- **Semantic Analysis & Catalog Lookup:**
  - Predefined Catalog: `students`, `departments`, `courses`, `enrollments`.
  - Validates relation existence.
  - Validates attribute existence within the resolved table.
  - Prevents ambiguous projection semantics (e.g., `SELECT *, name`).

---

## Slide 8: Interactive Web Studio & Visual AST Flowchart
- **Visual AST Renderer:** Renders AST hierarchies as an orthogonal arrow flowchart tree with color-coded nodes:
  - **Dark Blue Pills:** Clause Root Nodes (`SelectQuery`, `Projections`, `From`, `Where`).
  - **Red Pills:** Identifiers & Tables (`Table(students)`, `Identifier(age)`).
  - **Blue Pills:** Projected Arguments (`Identifier(name)`).
  - **Green Pills:** Literals & Binary Operators (`BinaryExpr(>=)`, `Literal(20)`).
- **Modern Ergonomics:** Responsive split-pane layout, real-time token inspections, and Dark/Light theme toggling.

---

## Slide 9: CLI REPL, Demo Runner & Test Verification Protocol
- **Interactive Multi-Line Shell (`python run.py --cli`):**
  - Prompt commands: `.help`, `.tables`, `.schema`, `.members`, `.clear`, `.exit`.
  - Multi-line query buffering until semicolon `;` terminator.
- **Test Execution Matrix:**
  - **45 Formally Documented Test Cases:** Functional queries (`TC-VAL`), Negative diagnostic queries (`TC-INV`), and Boundary edge cases (`TC-EDGE`).
  - **Automated Regression Suite:** 46 passing unit tests and 5 golden reference AST fixtures (`tests/test_golden_ast.py`).

---

## Slide 10: Individual Member Contributions
- **Transparent Division of Responsibility:**
  - *Geo Cherian Mathew:* Core compiler engine, CFG, LL(1) parser, AST generator, semantic analyzer, Web IDE & CLI.
  - *Liya Tomy:* Project README, Git workflow setup, documentation standards.
  - *Elkin Wilson George:* Language boundary definitions, academic report chapters 1 to 3.
  - *Joswin Joshy:* Token regex design, lexical specification, academic report chapters 4 to 6.
  - *Jonathan Kuruvilla Thomas:* Valid test query matrix, presentation slides outline.
  - *Justin Mathew Philip:* Invalid test query suite, diagnostic matrix, and viva examination guide.

---

## Slide 11: Conclusion & Future Scope
- **Project Achievements:** 
  - Complete, zero-dependency compiler front-end operating from first principles.
  - Comprehensive negative testing and pinpoint diagnostic reporting.
  - Dual interfaces: Interactive terminal REPL + modern browser-based Web Studio.
- **Future Extensions:**
  - Adding relational `JOIN` syntax and cross-table semantic resolution.
  - Intermediate Representation (IR) generation (Relational Algebra execution plans).
  - Code generation to a bytecode virtual machine or SQLite-compatible execution backend.
