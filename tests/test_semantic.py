"""
Unit tests for the Semantic Analyzer and Schema Validation.
"""

import unittest
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.semantic.schema import get_default_catalog


class TestSemanticAnalyzer(unittest.TestCase):

    def setUp(self):
        self.catalog = get_default_catalog()
        self.analyzer = SemanticAnalyzer(self.catalog)

    def test_valid_query_resolution(self):
        query = "SELECT id, name, gpa FROM students WHERE age >= 18 AND gpa > 3.0 ORDER BY name ASC;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.errors), 0)
        self.assertEqual(report.resolved_table, "students")
        self.assertEqual(report.resolved_columns, ["id", "name", "gpa"])

    def test_wildcard_expansion(self):
        query = "SELECT * FROM employees;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertTrue(report.is_valid)
        self.assertEqual(
            report.resolved_columns,
            ["emp_id", "name", "salary", "department", "age"],
        )

    def test_table_not_found_error(self):
        query = "SELECT id FROM nonexistent_table;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0].code, "TABLE_NOT_FOUND")
        self.assertIn("nonexistent_table", report.errors[0].message)

    def test_column_not_found_in_projections(self):
        query = "SELECT id, imaginary_col FROM students;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.errors[0].code, "COLUMN_NOT_FOUND")
        self.assertIn("imaginary_col", report.errors[0].message)

    def test_column_not_found_in_where(self):
        query = "SELECT name FROM students WHERE fake_column >= 10;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.errors[0].code, "COLUMN_NOT_FOUND")
        self.assertIn("fake_column", report.errors[0].message)

    def test_column_not_found_in_order_by(self):
        query = "SELECT name FROM students ORDER BY ghost_column DESC;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.errors[0].code, "COLUMN_NOT_FOUND")
        self.assertIn("ghost_column", report.errors[0].message)

    def test_type_mismatch_numeric_vs_string(self):
        # age is INTEGER, 'twenty' is STRING
        query = "SELECT name FROM students WHERE age = 'twenty';"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.errors[0].code, "TYPE_MISMATCH")
        self.assertIn("Cannot compare column 'age' (INTEGER) with literal 'twenty' (STRING)", report.errors[0].message)

    def test_type_mismatch_string_vs_number(self):
        # name is STRING, 42 is INTEGER
        query = "SELECT id FROM students WHERE name > 42;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertFalse(report.is_valid)
        self.assertEqual(report.errors[0].code, "TYPE_MISMATCH")
        self.assertIn("Cannot compare column 'name' (STRING) with literal 42 (INTEGER)", report.errors[0].message)

    def test_duplicate_projection_warning(self):
        query = "SELECT name, age, name FROM students;"
        ast = Parser.from_source(query).parse()
        report = self.analyzer.analyze(ast)

        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("Duplicate projection of column 'name'", report.warnings[0])


if __name__ == "__main__":
    unittest.main()
