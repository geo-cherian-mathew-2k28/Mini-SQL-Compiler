"""
Automated regression tests comparing live parser AST outputs against Golden JSON fixtures.
"""

import json
import os
import unittest
from src.parser.parser import Parser

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "ast_references")


class TestGoldenAST(unittest.TestCase):

    def _compare_with_golden(self, query: str, filename: str):
        path = os.path.join(GOLDEN_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            expected_ast = json.load(f)

        actual_ast = Parser.from_source(query).parse().to_dict()
        self.assertEqual(actual_ast, expected_ast, f"Mismatch in {filename}")

    def test_golden_simple_select(self):
        self._compare_with_golden("SELECT id, name FROM users;", "simple_select.json")

    def test_golden_wildcard_select(self):
        self._compare_with_golden("SELECT * FROM customers;", "wildcard_select.json")

    def test_golden_where_simple(self):
        self._compare_with_golden("SELECT id FROM orders WHERE amount > 100;", "where_simple.json")

    def test_golden_where_compound(self):
        self._compare_with_golden(
            "SELECT id FROM logs WHERE level = 'ERROR' AND code = 500;",
            "where_compound.json",
        )

    def test_golden_full_query(self):
        self._compare_with_golden(
            "SELECT name, score FROM students WHERE score >= 50 ORDER BY score DESC;",
            "full_query.json",
        )


if __name__ == "__main__":
    unittest.main()
