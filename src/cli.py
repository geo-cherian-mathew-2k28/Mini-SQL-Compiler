"""
Interactive Shell & Command-Line Interface (CLI) for the Mini SQL Compiler.
Features:
- Interactive REPL with multi-line SQL input
- Team member attribution banner
- Single-query execution mode
- Schema introspection (.tables, .schema)
- Direct error diagnosis and AST inspection
"""

import sys
import os
import argparse
from typing import List
from src.compiler import MiniSQLCompiler
from src.semantic.schema import get_default_catalog

TEAM_MEMBERS: List[str] = [
    "Geo Cherian Mathew",
    "Liya Tomy",
    "Elkin Wilson George",
    "Joswin Joshy",
    "Jonathan Kuruvilla Thomas",
    "Justin Mathew Philip",
]

def print_banner():
    banner = r"""
========================================================================================
  __  __ ___ _   _ ___   ____   ___  _        ____ ___  __  __ ____ ___ _     _____ ____  
 |  \/  |_ _| \ | |_ _| / ___| / _ \| |      / ___/ _ \|  \/  |  _ \_ _| |   | ____|  _ \ 
 | |\/| || ||  \| || |  \___ \| | | | |     | |  | | | | |\/| | |_) | || |   |  _| | |_) |
 | |  | || || |\  || |   ___) | |_| | |___  | |__| |_| | |  | |  __/| || |___| |___|  _ < 
 |_|  |_|___|_| \_|___| |____/ \__\_\_____|  \____\___/|_|  |_|_|  |___|_____|_____|_| \_\

  Compiler Design Mini-Project — 3rd Year Computer Science and Engineering
========================================================================================
  Project Team Members:
"""
    print(banner)
    for idx, member in enumerate(TEAM_MEMBERS, 1):
        print(f"    [{idx}] {member}")
    print("========================================================================================\n")


def print_help():
    print("""
Mini SQL Compiler Shell Commands:
  .help      Show this help message
  .tables    List all available database tables
  .schema    Display full schema definitions with column data types
  .members   List project team members
  .clear     Clear the terminal screen
  .exit      Exit the compiler shell (or type .quit / Ctrl+C)

Query Guidelines:
  - Statements must start with 'SELECT' and end with ';'
  - Clause order: SELECT -> FROM -> [WHERE] -> [ORDER BY] -> ';'
  - Example: SELECT name, age FROM students WHERE age >= 18 ORDER BY name ASC;
""")


def print_schema():
    catalog = get_default_catalog()
    print("\n--- Available Database Tables & Schema ---")
    for tbl in catalog.get_all_tables():
        print(f"\n  Table: {tbl.name}")
        for col in tbl.columns.values():
            null_str = "NULL" if col.nullable else "NOT NULL"
            print(f"    - {col.name:<15} {col.data_type:<10} ({null_str})")
    print("------------------------------------------\n")


def execute_query(query: str, verbose: bool = False):
    compiler = MiniSQLCompiler()
    result = compiler.compile(query)

    print(f"\n[*] Query: {result.query}")

    # Stage 1: Lexical
    print(f"\n--- [Stage 1: Lexical Analysis] ---")
    print(f"Total Tokens: {len(result.tokens)}")
    if verbose or len(result.tokens) <= 20:
        for idx, t in enumerate(result.tokens):
            print(f"  [{idx+1:02d}] {t['type']:<16} Lexeme: {t['lexeme']!r:<14} (Line {t['line']}, Col {t['column']})")

    # Stage 2: Syntax Analysis & Parse Tree
    print(f"\n--- [Stage 2: Syntax Analysis & Parse Tree] ---")
    if result.parse_tree_pretty:
        print(result.parse_tree_pretty)
    elif result.ast_pretty:
        print(result.ast_pretty)
    else:
        print("  [!] Parse tree not generated due to syntax errors.")

    # Stage 3: Semantic
    print(f"--- [Stage 3: Semantic Analysis] ---")
    if result.semantic_report:
        sr = result.semantic_report
        status = "PASSED" if sr["is_valid"] else "FAILED"
        print(f"Status           : {status}")
        print(f"Resolved Table   : {sr['resolved_table']}")
        print(f"Resolved Columns : {', '.join(sr['resolved_columns'])}")
        if sr["warnings"]:
            for w in sr["warnings"]:
                print(f"  [WARNING] {w}")

    # Final Outcome Banner
    if result.success:
        print(f"\n[OK] COMPILATION SUCCESSFUL — All front-end stages validated.\n")
    else:
        print(f"\n[X] COMPILATION FAILED:")
        for err in result.errors:
            loc = f" at line {err['line']}, column {err['column']}" if err.get("line") else ""
            print(f"    [{err['stage']}] {err['message']}{loc}")
        print()

    return result.success


def start_interactive_repl():
    print_banner()
    print("Welcome to the interactive Mini SQL Compiler Shell.")
    print("Type your SQL query (end with ';') or type '.help', '.tables', '.exit'.\n")

    query_buffer = []

    while True:
        try:
            prompt = "SQL> " if not query_buffer else " ...> "
            line = input(prompt).strip()

            if not query_buffer and line.startswith("."):
                cmd = line.lower()
                if cmd in (".exit", ".quit"):
                    print("Exiting Mini SQL Compiler Shell. Goodbye!")
                    break
                elif cmd == ".help":
                    print_help()
                    continue
                elif cmd == ".tables":
                    catalog = get_default_catalog()
                    print("Tables:", ", ".join(t.name for t in catalog.get_all_tables()))
                    continue
                elif cmd == ".schema":
                    print_schema()
                    continue
                elif cmd == ".members":
                    print("\nProject Team Members:")
                    for idx, m in enumerate(TEAM_MEMBERS, 1):
                        print(f"  {idx}. {m}")
                    print()
                    continue
                elif cmd == ".clear":
                    os.system("cls" if os.name == "nt" else "clear")
                    print_banner()
                    continue
                else:
                    print(f"Unknown command: '{line}'. Type '.help' for instructions.")
                    continue

            if not line and not query_buffer:
                continue

            query_buffer.append(line)

            # Check if current line contains a statement terminator ';'
            if ";" in line:
                full_query = " ".join(query_buffer)
                query_buffer = []
                execute_query(full_query, verbose=True)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting shell. Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="Mini SQL Compiler CLI & Interactive Shell")
    parser.add_argument("query", nargs="?", type=str, help="SQL Query to compile (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detailed token output")
    args = parser.parse_args()

    if args.query:
        # Single-shot execution mode
        print_banner()
        success = execute_query(args.query, verbose=args.verbose)
        sys.exit(0 if success else 1)
    else:
        # Interactive REPL mode
        start_interactive_repl()


if __name__ == "__main__":
    main()
