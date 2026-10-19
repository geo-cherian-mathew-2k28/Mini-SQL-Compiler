"""
Command-Line Interface (CLI) for the Mini SQL Compiler.
Allows quick terminal compilation, token inspection, and AST visualization.
"""

import sys
import argparse
import json
from src.compiler import MiniSQLCompiler


def print_banner():
    banner = r"""
========================================================================
   __  __ _       _    ____   ___  _        ____                            _ _           
  |  \/  (_)_ __ (_)  / ___| / _ \| |      / ___|___  _ __ ___  _ __  _   | | | ___ _ __ 
  | |\/| | | '_ \| |  \___ \| | | | |     | |   / _ \| '_ ` _ \| '_ \| | | | | |/ _ \ '__|
  | |  | | | | | | |   ___) | |_| | |___  | |__| (_) | | | | | | |_) | |_| | | |  __/ |   
  |_|  |_|_|_| |_|_|  |____/ \__\_\_____|  \____\___/|_| |_| |_| .__/ \__,_|_|_|\___|_|   
                                                               |_|                        
  Compiler Design Mini-Project — 3rd Year CSE Front-End Engine
========================================================================
"""
    print(banner)


def run_cli(query: str, verbose: bool = False):
    print_banner()
    print(f"[*] Input Query:\n    {query}\n")

    compiler = MiniSQLCompiler()
    result = compiler.compile(query)

    # 1. Lexical Stage
    print(f"--- [Stage 1: Lexical Analysis] ---")
    print(f"Total Tokens Emitted: {len(result.tokens)}")
    if verbose:
        for i, t in enumerate(result.tokens):
            print(f"  [{i:02d}] {t['type']:<15} Lexeme: {t['lexeme']!r:<12} (Line {t['line']}, Col {t['column']})")

    # 2. Syntax Stage
    print(f"\n--- [Stage 2: Syntax Analysis & AST Construction] ---")
    if result.ast_pretty:
        print(result.ast_pretty)
    else:
        print("  AST Generation Skipped due to earlier errors.")

    # 3. Semantic Stage
    print(f"--- [Stage 3: Semantic Analysis] ---")
    if result.semantic_report:
        sr = result.semantic_report
        status = "PASSED" if sr["is_valid"] else "FAILED"
        print(f"Validation Status : {status}")
        print(f"Resolved Table    : {sr['resolved_table']}")
        print(f"Resolved Columns  : {', '.join(sr['resolved_columns'])}")
        if sr["warnings"]:
            for w in sr["warnings"]:
                print(f"  [WARNING] {w}")

    # Errors Summary
    if not result.success:
        print(f"\n====================== COMPILATION FAILED ======================")
        for err in result.errors:
            loc = f" (Line {err['line']}, Col {err['column']})" if err.get("line") else ""
            print(f"  [!] [{err['stage']}] {err['message']}{loc}")
        print("================================================================")
        sys.exit(1)
    else:
        print(f"\n===================== COMPILATION SUCCESSFUL =====================")
        print(f"  All compiler front-end stages completed without errors.")
        print("==================================================================")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Mini SQL Compiler CLI")
    parser.add_argument("query", nargs="?", type=str, help="SQL Query to compile")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display full token stream details")
    args = parser.parse_args()

    if not args.query:
        # Default showcase query
        sample = "SELECT name, age FROM students WHERE age >= 18 AND gpa > 3.0 ORDER BY name ASC;"
        print("[!] No query argument passed. Executing default showcase query:\n")
        run_cli(sample, verbose=True)
    else:
        run_cli(args.query, verbose=args.verbose)


if __name__ == "__main__":
    main()
