# Documentation Directory Overview

This directory houses the formal academic, theoretical, specification, and presentation documents for the **Mini SQL Compiler** project.

## Directory Structure

```text
docs/
├── grammar/                  # Formal language theory, CFG, and transformations
│   ├── cfg.md               # Context-Free Grammar (BNF notation)
│   ├── transformations.md   # Left-recursion elimination, left-factoring, FIRST/FOLLOW
│   └── parse_trees.md       # Parse tree vs. AST manual derivations
├── presentation/             # Presentation slides & viva voce preparation
│   ├── slides_outline.md    # 11-slide presentation script
│   └── viva_questions.md    # 18 foundational & member-tailored viva questions
├── report/                   # Master academic report & contribution audit
│   ├── project_report.md    # Full academic project report (Chapters 1-9)
│   └── contributions.md     # Individual contribution ledger & role audit
├── tests/                    # Testing protocols & verification matrix
│   └── test_matrix.md       # Master 45-test case execution matrix
└── sql_specification.md      # Language boundaries, supported clauses, & catalog
```

Each subdirectory corresponds to specific academic evaluation criteria outlined in the 3rd-year Computer Science & Engineering Compiler Design syllabus.

## Quick Execution Launchers

For laboratory evaluation, viva voce examinations, and quick demonstrations on Windows machines, two one-click root launchers are provided:

- `start_studio.bat`: Standard Windows Command Prompt batch launcher. Double-click or run from CMD to check Python prerequisites and interactively choose between Web Studio IDE (default) and Interactive CLI REPL.
- `start_studio.ps1`: Modern PowerShell launcher with formatted, colored console diagnostics.

### Execution Instructions

```powershell
# Windows Command Prompt or File Explorer Double-Click
start_studio.bat

# Windows PowerShell
.\start_studio.ps1

# PowerShell with ExecutionPolicy bypass (if scripts are restricted on lab machines)
powershell -ExecutionPolicy Bypass -File .\start_studio.ps1
```

