"""
Unit tests for the Demonstration Runner (demo_runner.py).
Verifies that all curated showcase queries run cleanly and meet acceptance criteria.
"""

import io
import sys
import unittest
from demo_runner import DEMO_QUERIES, run_demo
from src.compiler import MiniSQLCompiler


class TestDemoRunner(unittest.TestCase):

    def setUp(self):
        self.compiler = MiniSQLCompiler()

    def test_demo_query_count(self):
        """Verify that exactly 5 representative queries are defined."""
        self.assertEqual(len(DEMO_QUERIES), 5)

    def test_demo_query_structure(self):
        """Verify the 5 expected queries are defined as requested."""
        expected_queries = [
            "SELECT name, age FROM students;",
            "SELECT * FROM courses;",
            "SELECT name, gpa FROM students WHERE age >= 18 AND gpa >= 3.5;",
            "SELECT name, building FROM departments ORDER BY building ASC;",
            "SELECT name WHERE age > 20 FROM students;",
        ]
        actual_queries = [q["sql"] for q in DEMO_QUERIES]
        self.assertEqual(actual_queries, expected_queries)

    def test_query_1_basic_projection(self):
        res = self.compiler.compile(DEMO_QUERIES[0]["sql"])
        self.assertTrue(res.success)
        self.assertEqual(res.stage_reached, "COMPLETED")
        self.assertEqual(res.semantic_report["resolved_columns"], ["name", "age"])

    def test_query_2_wildcard_projection(self):
        res = self.compiler.compile(DEMO_QUERIES[1]["sql"])
        self.assertTrue(res.success)
        self.assertEqual(res.stage_reached, "COMPLETED")
        self.assertIn("title", res.semantic_report["resolved_columns"])

    def test_query_3_compound_where(self):
        res = self.compiler.compile(DEMO_QUERIES[2]["sql"])
        self.assertTrue(res.success)
        self.assertEqual(res.stage_reached, "COMPLETED")

    def test_query_4_order_by(self):
        res = self.compiler.compile(DEMO_QUERIES[3]["sql"])
        self.assertTrue(res.success)
        self.assertEqual(res.stage_reached, "COMPLETED")
        self.assertEqual(res.semantic_report["resolved_table"], "departments")

    def test_query_5_syntax_error_diagnosis(self):
        res = self.compiler.compile(DEMO_QUERIES[4]["sql"])
        self.assertFalse(res.success)
        self.assertEqual(res.stage_reached, "SYNTAX_FAILED")
        self.assertTrue(any(e["stage"] == "Syntax Analysis" for e in res.errors))

    def test_run_demo_execution(self):
        """Verify run_demo executes and returns 0 without raising exceptions."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exit_code = run_demo(verbose=False)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(exit_code, 0)
        self.assertIn("DEMONSTRATION BATCH SCORECARD", output)
        self.assertIn("All 5 showcase queries executed cleanly", output)


if __name__ == "__main__":
    unittest.main()
