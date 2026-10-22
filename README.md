# Mini SQL Compiler
 
A compiler front-end for a small subset of SQL, written in Python with no third-party dependencies. It takes a `SELECT` query through lexical analysis, parsing, AST generation, and semantic analysis, and reports errors at each stage.
 
This is a 3rd Year Computer Science and Engineering Compiler Design mini-project.
 
## Table of Contents
 
- [Academic Context and Objectives](#academic-context-and-objectives)
- [Project Scope](#project-scope)
- [Compiler Front-End Phases](#compiler-front-end-phases)
- [Supported SQL](#supported-sql)
- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Project Milestones](#project-milestones)
- [Team and Contributions](#team-and-contributions)
## Academic Context and Objectives
 
This project is submitted as the mini-project for the Compiler Design course in the 3rd year of the B.Tech Computer Science and Engineering programme.
 
Objectives:
 
- Apply compiler design theory by building the front-end of a compiler for a real language (a subset of SQL)
- Define a formal context-free grammar and transform it for top-down parsing (left-recursion elimination and left-factoring)
- Implement a lexer, a recursive-descent parser, and a semantic analyzer
- Represent queries as an Abstract Syntax Tree (AST) and validate them against a schema
- Produce clear, stage-specific error diagnostics
- Verify the implementation with automated tests
## Project Scope
 
In scope: the compiler front-end for a single `SELECT` statement.
 
Out of scope: query execution, optimization, code generation, `JOIN`, subqueries, `GROUP BY`, aggregates, and data-modification statements (`INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`).
 
The compiler validates queries; it does not run them against data.
 
## Compiler Front-End Phases
 
1. **Lexical Analysis (Lexing):** the scanner reads the query text and produces tokens (keywords, identifiers, literals, operators, punctuation) with line and column positions. Invalid characters are reported as lexical errors.
2. **Syntax Analysis (Parsing):** a recursive-descent parser checks the token stream against the grammar. Malformed queries are reported as syntax errors that state what was expected and what was found.
3. **AST Generation:** a successful parse produces an Abstract Syntax Tree that captures the query's structure (projections, source table, `WHERE` condition, `ORDER BY`).
4. **Semantic Analysis:** the AST is checked against a schema catalog (symbol table) to confirm that the table and columns exist and that comparisons use compatible types.
Each phase stops the pipeline on failure and reports its errors, so a query only reaches the next phase if the previous one succeeded.
 
## Supported SQL
 
```sql
SELECT <columns | *>
FROM <table>
[WHERE <condition>]
[ORDER BY <column> [ASC | DESC], ...]
[;]
```
 
- Keywords are case-insensitive: `SELECT`, `FROM`, `WHERE`, `ORDER`, `BY`, `ASC`, `DESC`, `AND`, `OR`
- Comparison operators: `=`, `!=`, `<>`, `<`, `<=`, `>`, `>=`
- `AND` and `OR` with parentheses (`AND` binds tighter than `OR`)
- Integer, float, and `'string'` literals
The semantic checks use a built-in demo schema with relational tables including `students`, `employees`, `orders`, `products`, `departments`, and `courses`.
 
## Installation
 
Requires Python 3.8 or newer.
 
```bash
git clone https://github.com/geo-cherian-mathew-2k28/Mini-SQL-Compiler.git
cd Mini-SQL-Compiler
```
 
## Usage
 
### Quick Launchers (One-Click)
 
For rapid viva evaluation and classroom demos without manual terminal flags:
 
- **Interactive Studio Launcher**: Double-click `start_studio.bat` or run `.\start_studio.ps1`
- **Automated Demonstration Runner Launcher**: Double-click `run_demo.bat` or run `.\run_demo.ps1`
 
### Manual Terminal Execution
 
Start the web interface (opens at http://127.0.0.1:5000):
 
```bash
python run.py
```
 
Run the command-line shell:
 
```bash
python run.py --cli
```
 
Compile a single query:
 
```bash
python run.py --cli "SELECT name, age FROM students WHERE age >= 18 ORDER BY name ASC;"
```
 
### Automated Demonstration Runner (Viva & Evaluation Showcase)
Execute a curated batch of 5 representative demonstration queries (simple projection, wildcard expansion, compound WHERE filtering, ORDER BY sorting, and syntax error diagnosis) with one single command:

```bash
python demo_runner.py
```

For detailed token classifications and pretty-printed ASTs:

```bash
python demo_runner.py --verbose
```

A reference implementation of the same grammar using Flex and Bison is in `c_lex_yacc/` (see the README in that folder).
 
## Running Tests
 
```bash
python -m unittest discover -s tests -t .
```
 
## Project Structure
 
```
Mini-SQL-Compiler/
├── start_studio.bat  # Windows Command Prompt quick launcher (Studio/CLI)
├── start_studio.ps1  # Windows PowerShell quick launcher (Studio/CLI)
├── run_demo.bat      # Windows Command Prompt quick demo launcher
├── run_demo.ps1      # Windows PowerShell quick demo launcher
├── demo_runner.py    # Automated viva demonstration showcase runner
├── run.py            # Main application entry point
├── src/
│   ├── lexer/        # Tokens and scanner
│   ├── parser/       # Recursive-descent parser
│   ├── ast/          # AST nodes
│   ├── semantic/     # Schema and semantic analyzer
│   ├── compiler.py   # Pipeline driver
│   ├── cli.py        # Command-line shell
│   └── ui/           # Web server
├── web/              # Web interface
├── c_lex_yacc/       # Flex/Bison implementation
├── docs/grammar/     # Grammar documentation
└── tests/            # Tests and AST fixtures
```
 
## Documentation
 
- [Context-Free Grammar](docs/grammar/cfg.md)
- [Grammar Transformations](docs/grammar/transformations.md)
- [Parse Trees and ASTs](docs/grammar/parse_trees.md)
## Project Milestones
 
| Milestone | Date |
|-----------|------|
| Project presentation | 23 October 2026 |
 
## Team and Contributions
 
| Member | Team | Contribution |
|--------|------|--------------|
| Geo Cherian Mathew | Core Compiler | Core compiler implementation, parser, AST, and integration (Issues #4, #5, #7, #11) |
| Joswin Joshy | Core Compiler | Core compiler implementation, parser, AST, and integration (Issues #4, #5, #7, #11) |
| Elkin Wilson George | Report | Supported SQL features documentation (Issue #2) and token classification table (Issue #6), forming Chapters 2 and 4 of the report |
| Liya Tomy | Report | Project README and scope (Issue #1) and compiling the report draft in `docs/report/` (Issue #14) |
| Jonathan Kuruvilla Thomas | Presentation | Valid SQL test queries for the demo (Issue #8), demonstration runner showcase script (demo_runner.py), and presentation slide outline (Issue #13) |
| Justin Mathew Philip | Presentation | Invalid SQL queries showing syntax errors on slides (Issue #9) and viva questions and answers preparation (Issue #13) |
