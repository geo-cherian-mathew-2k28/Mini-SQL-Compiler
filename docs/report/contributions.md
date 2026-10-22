# Group Contribution Ledger & Individual Contribution Audit

**Course:** 3rd Year B.Tech Computer Science & Engineering  
**Project:** Mini SQL Compiler Front-End Architecture  
**Evaluation Date:** 23 October 2026  
**Repository:** `https://github.com/geo-cherian-mathew-2k28/Mini-SQL-Compiler`

---

## 1. Master Contribution Summary Matrix

| Member Name | Role & Core Responsibility | Assigned GitHub Issues | Deliverables & Artifacts | Viva Defense Focus Area |
| :--- | :--- | :--- | :--- | :--- |
| **Geo Cherian Mathew** | Compiler Design & Core Architecture | #4, #5, #7, #11, #18, #19, #20, #21, #2, #3, #9, #10, #12, #13, #14 | Lexer, Recursive-Descent Parser, AST Nodes, Semantic Analyzer, CLI REPL, Web Studio IDE, CFG specs, Transformations, Golden AST suite, Invalid & Edge test suites, Master Test Matrix, Report & Viva guides | Top-Down LL(1) Parsing, Left-Recursion Elimination, Precedence Climbing, AST synthesis |
| **Liya Tomy** | Project Documentation & Guidelines | #1 | `README.md` (Project overview, setup instructions, academic context) | High-level compiler front-end phases, project scope, repository governance |
| **Elkin Wilson George** | SQL Specification & Report Lead (Part 1) | #2, #14 | `docs/sql_specification.md`, Project Report Chapters 1–3 (Introduction, Grammar Theory, Lexical Design) | Mandatory clause ordering (`SELECT -> FROM -> WHERE -> ORDER BY`), language boundaries |
| **Joswin Joshy** | Lexical Specification & Report Lead (Part 2) | #6, #8, #14 | `docs/grammar/tokens.md`, `tests/test_valid.sql`, Project Report Chapters 4–6 (Parser Architecture, AST Design, Semantic Checks) | Regular expressions, Token classification, Lookahead disambiguation (`>=` vs `>`) |
| **Jonathan Kuruvilla Thomas** | Test Suites & Presentation Architecture | #8, #13 | `tests/test_valid.sql`, `docs/presentation/slides_outline.md`, `demo_runner.py` | Positive test case design, AST structural verification, automated viva demonstration runner, Presentation slide script |
| **Justin Mathew Philip** | Negative Testing & Viva Preparation | #9, #10, #12 | `tests/test_invalid.sql`, `tests/test_edge_cases.sql`, `docs/presentation/viva_questions.md` | Negative test design, Diagnostic error classification, Viva voce examination theory |

---

## 2. Auditable Deliverables Traceability

### Phase 1: Grammar & Theoretical Foundations
- `docs/grammar/cfg.md`: Context-Free Grammar specified in Backus-Naur Form (BNF).
- `docs/grammar/transformations.md`: Left-recursion elimination proofs, left-factoring, and FIRST/FOLLOW set mathematical calculations.
- `docs/grammar/parse_trees.md`: Step-by-step concrete parse tree vs. abstract syntax tree derivations.
- `docs/sql_specification.md`: Formal language specification, supported constructs, and explicit out-of-scope boundaries.

### Phase 2: Compiler Front-End Implementation
- `src/lexer/tokens.py` & `src/lexer/lexer.py`: Lexical analysis engine emitting 1-based coordinate tokens with 2-character lookahead.
- `src/ast/nodes.py` & `src/parser/parser.py`: Deterministic recursive descent parser producing structured AST nodes.
- `src/semantic/schema.py` & `src/semantic/analyzer.py`: In-memory schema catalog and semantic verification engine.
- `c_lex_yacc/`: Parallel reference implementation (`lexer.l`, `parser.y`, `ast.h`, `ast.c`) for traditional UNIX lab evaluators.

### Phase 3: Interactive User Interfaces & Diagnostics
- `src/cli.py` & `run.py --cli`: Interactive multi-line REPL shell supporting terminal commands (`.tables`, `.schema`, `.members`, `.clear`).
- `src/ui/server.py` & `web/`: Zero-dependency Web Studio IDE featuring a dynamic, orthogonal arrow flowchart AST tree visualizer and Light/Dark theme toggle.

### Phase 4: Quality Assurance & Academic Reporting
- `tests/test_lexer.py`, `tests/test_parser.py`, `tests/test_semantic.py`, `tests/test_golden_ast.py`: 46 automated unit tests.
- `tests/test_invalid.sql` & `tests/test_invalid_expected.md`: Negative test suite covering 22 diagnostic failure modes.
- `tests/test_edge_cases.sql` & `tests/edge_cases_notes.md`: Boundary condition suite testing whitespace, lookaheads, and boolean precedence.
- `docs/tests/test_matrix.md`: Master 45-query test execution matrix.
- `docs/presentation/slides_outline.md` & `docs/presentation/viva_questions.md`: Evaluation defense slides and 18 viva questions.
- `docs/report/project_report.md`: Master academic project report following university formatting standards.
