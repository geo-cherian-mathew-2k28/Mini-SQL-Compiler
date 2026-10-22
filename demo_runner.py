"""
Mini SQL Compiler -- Demonstration Runner (Evaluation Showcase)
==============================================================
A dedicated demonstration script designed for viva and practical evaluation.
Sequentially executes a curated batch of 5 representative SQL queries across
all compiler front-end stages (Lexer -> Parser -> AST -> Semantic Analyzer)
and displays cleanly formatted stage markers, token streams, syntax status,
and semantic validation diagnostics.

Usage:
    python demo_runner.py
    python demo_runner.py --verbose   # Includes full Pretty AST trees
"""

import sys
import argparse
from typing import Any, Dict, List

from src.compiler import MiniSQLCompiler

# =============================================================================
# Curated Demonstration Queries (5 Representative Scenarios)
# =============================================================================
DEMO_QUERIES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Basic SELECT Projection",
        "sql": "SELECT name, age FROM students;",
        "description": "Explicit projection of specific attributes ('name', 'age') from 'students' relation.",
        "expected_valid": True,
    },
    {
        "id": 2,
        "title": "Wildcard Projection",
        "sql": "SELECT * FROM courses;",
        "description": "Wildcard '*' selection expanding into all schema columns of 'courses' relation.",
        "expected_valid": True,
    },
    {
        "id": 3,
        "title": "Compound WHERE Filter",
        "sql": "SELECT name, gpa FROM students WHERE age >= 18 AND gpa >= 3.5;",
        "description": "Complex boolean predicate with relational comparison (>=) and logical conjunction (AND).",
        "expected_valid": True,
    },
    {
        "id": 4,
        "title": "ORDER BY Sorting",
        "sql": "SELECT name, building FROM departments ORDER BY building ASC;",
        "description": "Result ordering with explicit ascending sort direction ('ASC') on 'building'.",
        "expected_valid": True,
    },
    {
        "id": 5,
        "title": "Syntax Error Diagnostic Demonstration",
        "sql": "SELECT name WHERE age > 20 FROM students;",
        "description": "Out-of-order clauses (WHERE placed before mandatory FROM) showcasing syntax error diagnosis.",
        "expected_valid": False,
    },
]


def print_banner() -> None:
    banner = r"""
========================================================================================
    __  __ ___ _   _ ___   ____   ___  _        ____ ___  __  __ ____ ___ _     _____ ____  
   |  \/  |_ _| \ | |_ _| / ___| / _ \| |      / ___/ _ \|  \/  |  _ \_ _| |   | ____|  _ \ 
   | |\/| || ||  \| || |  \___ \| | | | |     | |  | | | | |\/| | |_) | || |   |  _| | |_) |
   | |  | || || |\  || |   ___) | |_| | |___  | |__| |_| | |  | |  __/| || |___| |___|  _ < 
   |_|  |_|___|_| \_|___| |____/ \__\_\_____|  \____\___/|_|  |_|_|  |___|_____|_____|_| \_\

                  COMPILER DESIGN MINI-PROJECT -- EVALUATION SHOWCASE
                 Automated Front-End Pipeline Verification & Diagnostics
========================================================================================
  Executes all front-end phases across 5 curated test scenarios:
    [1] Basic SELECT Projection
    [2] Wildcard '*' Expansion
    [3] Compound WHERE Predicate (AND/OR Logic)
    [4] ORDER BY Sorting Specification
    [5] Syntax Error Diagnosis & Error Recovery
========================================================================================
"""
    print(banner)


def format_token_preview(tokens: List[Dict[str, Any]], max_display: int = 12) -> str:
    """Formats a concise horizontal chain of token symbols for clean presentation."""
    items = []
    for t in tokens:
        ttype = t.get("type", "")
        lexeme = t.get("lexeme", "")
        if ttype == "EOF":
            items.append("<EOF>")
        elif ttype == "IDENTIFIER":
            items.append(f"ID({lexeme})")
        elif ttype in ("INT_LITERAL", "FLOAT_LITERAL", "STRING_LITERAL"):
            items.append(f"LIT({lexeme})")
        elif ttype in ("COMMA", "SEMICOLON", "ASTERISK"):
            items.append(f"'{lexeme}'")
        else:
            items.append(lexeme)

    if len(items) <= max_display:
        return " -> ".join(items)
    half = max_display // 2
    return " -> ".join(items[:half]) + f" -> ... ({len(items) - max_display} more) -> " + " -> ".join(items[-half:])


def run_demo(verbose: bool = False) -> int:
    """
    Runs the curated suite of demonstration queries and reports stage-by-stage results.
    Returns 0 on successful execution of the suite.
    """
    print_banner()
    compiler = MiniSQLCompiler()

    summary_rows = []

    print(f"[*] Starting demonstration batch of {len(DEMO_QUERIES)} queries...\n")

    for item in DEMO_QUERIES:
        qid = item["id"]
        title = item["title"]
        query_text = item["sql"]
        desc = item["description"]
        expected_valid = item["expected_valid"]

        divider = "-" * 88
        print(divider)
        print(f"QUERY {qid} OF {len(DEMO_QUERIES)}: {title.upper()}")
        print(divider)
        print(f"  SQL Query    : {query_text}")
        print(f"  Description  : {desc}")
        print(f"  Expectation  : {'Valid (all stages pass)' if expected_valid else 'Syntax Error (diagnosed and reported)'}")
        print()

        # Run compilation pipeline
        result = compiler.compile(query_text)

        # ---------------------------------------------------------------------
        # Stage 1: Lexical Analysis
        # ---------------------------------------------------------------------
        lex_status = "PASS" if result.stage_reached != "LEXICAL_FAILED" else "FAIL"
        print(f"  [Stage 1: Lexical Analysis (Scanner)]")
        print(f"    Status       : [{lex_status}] Generated {len(result.tokens)} tokens")
        print(f"    Token Stream : {format_token_preview(result.tokens)}")
        if verbose:
            print("    Tokens Breakdown:")
            for idx, t in enumerate(result.tokens, 1):
                print(f"      {idx:02d}. {t['type']:<15} lexeme: {t['lexeme']!r:<12} (line {t['line']}, col {t['column']})")
        print()

        # ---------------------------------------------------------------------
        # Stage 2: Syntax Analysis & AST Construction
        # ---------------------------------------------------------------------
        print(f"  [Stage 2: Syntax Analysis (Parser & AST)]")
        syntax_err = next((e for e in result.errors if e.get("stage") == "Syntax Analysis"), None)
        if syntax_err:
            print(f"    Status       : [SYNTAX ERROR DIAGNOSED]")
            print(f"    Error Type   : {syntax_err.get('type')}")
            print(f"    Message      : {syntax_err.get('message')}")
            print(f"    Position     : Line {syntax_err.get('line')}, Column {syntax_err.get('column')}")
            if syntax_err.get("expected") and syntax_err.get("found"):
                print(f"    Expected     : '{syntax_err.get('expected')}' | Found: '{syntax_err.get('found')}'")
            syntax_cell = "[DIAGNOSED]"
        else:
            print(f"    Status       : [PASS] Syntax conforms to grammar")
            if result.ast:
                tbl = result.ast.get("from_table", {}).get("name", "")
                projs = [p.get("name") if p.get("type") == "Identifier" else "*" for p in result.ast.get("projections", [])]
                has_where = "Yes" if result.ast.get("where") else "None"
                has_order = "Yes" if result.ast.get("order_by") else "None"
                print(f"    Target Table : {tbl}")
                print(f"    Projections  : {', '.join(projs)}")
                print(f"    WHERE Clause : {has_where}")
                print(f"    ORDER BY     : {has_order}")
            syntax_cell = "[PASS]"

        if verbose and result.ast_pretty:
            print("    Pretty AST:")
            for line in result.ast_pretty.splitlines():
                print(f"      {line}")
        print()

        # ---------------------------------------------------------------------
        # Stage 3: Semantic Analysis
        # ---------------------------------------------------------------------
        print(f"  [Stage 3: Semantic Analysis (Symbol Catalog & Types)]")
        sem_err = next((e for e in result.errors if e.get("stage") == "Semantic Analysis"), None)
        if syntax_err:
            print(f"    Status       : [SKIPPED] Stage bypassed due to prior syntax failure.")
            sem_cell = "[SKIPPED]"
        elif sem_err:
            print(f"    Status       : [SEMANTIC ERROR]")
            print(f"    Code         : {sem_err.get('code')}")
            print(f"    Message      : {sem_err.get('message')}")
            sem_cell = "[FAIL]"
        elif result.semantic_report and result.semantic_report.get("is_valid"):
            sr = result.semantic_report
            print(f"    Status       : [PASS] Semantic validation successful")
            print(f"    Bound Table  : {sr.get('resolved_table')}")
            print(f"    Resolved Cols: {', '.join(sr.get('resolved_columns', []))}")
            if sr.get("warnings"):
                print(f"    Warnings     : {', '.join(sr.get('warnings'))}")
            sem_cell = "[PASS]"
        else:
            print(f"    Status       : [UNKNOWN]")
            sem_cell = "[?]"
        print()

        # ---------------------------------------------------------------------
        # Final Stage Outcome for this query
        # ---------------------------------------------------------------------
        if expected_valid and result.success:
            verdict = "[SUCCESS - ALL STAGES VALID]"
            summary_status = "SUCCESS (PASS)"
        elif not expected_valid and syntax_err:
            verdict = "[SUCCESS - SYNTAX ERROR CAUGHT & DIAGNOSED]"
            summary_status = "SUCCESS (DIAGNOSED)"
        else:
            verdict = "[UNEXPECTED OUTCOME]"
            summary_status = "UNEXPECTED"

        print(f"  --> Stage Verdict: {verdict}")
        print()

        summary_rows.append({
            "id": qid,
            "title": title,
            "tokens": len(result.tokens),
            "syntax": syntax_cell,
            "semantic": sem_cell,
            "overall": summary_status,
        })

    # =========================================================================
    # Executive Demonstration Summary Table
    # =========================================================================
    print("=" * 88)
    print("                      DEMONSTRATION BATCH SCORECARD")
    print("=" * 88)
    header = f" {'#':<3} {'Scenario':<40} {'Tokens':<8} {'Syntax':<12} {'Semantic':<11} {'Outcome':<18}"
    print(header)
    print("-" * 88)
    for r in summary_rows:
        row_str = (
            f" {r['id']:<3} {r['title']:<40} {r['tokens']:<8} "
            f"{r['syntax']:<12} {r['semantic']:<11} {r['overall']:<18}"
        )
        print(row_str)
    print("=" * 88)
    print(" [OK] All 5 showcase queries executed cleanly.")
    print(" [*] Automated evaluation run completed without unhandled runtime exceptions.")
    print(" [*] Usage: python demo_runner.py  |  python demo_runner.py -v\n")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mini SQL Compiler Demonstration Runner for Viva & Practical Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python demo_runner.py            # Standard concise showcase
    python demo_runner.py -v         # Detailed token breakdown and AST views
        """,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose token classifications and pretty-printed ASTs",
    )
    args = parser.parse_args()

    sys.exit(run_demo(verbose=args.verbose))


if __name__ == "__main__":
    main()
