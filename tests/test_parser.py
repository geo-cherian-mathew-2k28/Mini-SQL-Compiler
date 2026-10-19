"""
Comprehensive unit tests for Syntax Analysis and AST Generation.
"""

import unittest
from src.parser.parser import Parser, SyntaxError
from src.ast.nodes import (
    SelectQuery,
    Wildcard,
    Identifier,
    Table,
    Literal,
    BinaryExpr,
    OrderByItem,
)


class TestParser(unittest.TestCase):

    # -------------------------------------------------------------------------
    # Positive Syntax Tests
    # -------------------------------------------------------------------------

    def test_minimal_select(self):
        query = "SELECT id FROM users;"
        ast = Parser.from_source(query).parse()

        self.assertIsInstance(ast, SelectQuery)
        self.assertEqual(len(ast.projections), 1)
        self.assertIsInstance(ast.projections[0], Identifier)
        self.assertEqual(ast.projections[0].name, "id")
        self.assertEqual(ast.from_table.name, "users")
        self.assertIsNone(ast.where)
        self.assertIsNone(ast.order_by)

    def test_wildcard_select(self):
        query = "SELECT * FROM employees"
        ast = Parser.from_source(query).parse()

        self.assertEqual(len(ast.projections), 1)
        self.assertIsInstance(ast.projections[0], Wildcard)
        self.assertEqual(ast.from_table.name, "employees")

    def test_multi_column_select(self):
        query = "SELECT id, name, salary FROM staff;"
        ast = Parser.from_source(query).parse()

        self.assertEqual(len(ast.projections), 3)
        self.assertEqual([p.name for p in ast.projections], ["id", "name", "salary"])

    def test_where_simple_comparison(self):
        query = "SELECT name FROM students WHERE age >= 18;"
        ast = Parser.from_source(query).parse()

        self.assertIsNotNone(ast.where)
        self.assertIsInstance(ast.where, BinaryExpr)
        self.assertEqual(ast.where.operator, ">=")
        self.assertEqual(ast.where.left.name, "age")
        self.assertEqual(ast.where.right.value, 18)

    def test_where_operator_precedence_and_over_or(self):
        # In G', AND binds tighter than OR: (a = 1) OR ((b = 2) AND (c = 3))
        query = "SELECT id FROM tbl WHERE a = 1 OR b = 2 AND c = 3;"
        ast = Parser.from_source(query).parse()

        self.assertIsInstance(ast.where, BinaryExpr)
        self.assertEqual(ast.where.operator, "OR")

        # Left side is a = 1
        self.assertEqual(ast.where.left.operator, "=")
        self.assertEqual(ast.where.left.left.name, "a")

        # Right side is (b = 2 AND c = 3)
        self.assertEqual(ast.where.right.operator, "AND")
        self.assertEqual(ast.where.right.left.left.name, "b")
        self.assertEqual(ast.where.right.right.left.name, "c")

    def test_where_parentheses_grouping(self):
        # Parentheses override precedence: ((a = 1) OR (b = 2)) AND (c = 3)
        query = "SELECT id FROM tbl WHERE (a = 1 OR b = 2) AND c = 3;"
        ast = Parser.from_source(query).parse()

        self.assertIsInstance(ast.where, BinaryExpr)
        self.assertEqual(ast.where.operator, "AND")

        # Left side is (a = 1 OR b = 2)
        self.assertEqual(ast.where.left.operator, "OR")
        # Right side is c = 3
        self.assertEqual(ast.where.right.operator, "=")

    def test_order_by_default_asc(self):
        query = "SELECT name FROM users ORDER BY age;"
        ast = Parser.from_source(query).parse()

        self.assertIsNotNone(ast.order_by)
        self.assertEqual(len(ast.order_by), 1)
        self.assertEqual(ast.order_by[0].column.name, "age")
        self.assertEqual(ast.order_by[0].direction, "ASC")

    def test_order_by_explicit_desc(self):
        query = "SELECT name FROM users ORDER BY age DESC;"
        ast = Parser.from_source(query).parse()

        self.assertEqual(ast.order_by[0].direction, "DESC")

    def test_order_by_multiple_columns(self):
        query = "SELECT name FROM employees ORDER BY department ASC, salary DESC;"
        ast = Parser.from_source(query).parse()

        self.assertEqual(len(ast.order_by), 2)
        self.assertEqual(ast.order_by[0].column.name, "department")
        self.assertEqual(ast.order_by[0].direction, "ASC")
        self.assertEqual(ast.order_by[1].column.name, "salary")
        self.assertEqual(ast.order_by[1].direction, "DESC")

    def test_full_query_pipeline(self):
        query = "SELECT name, age FROM students WHERE age >= 21 AND gpa > 3.5 ORDER BY gpa DESC;"
        ast = Parser.from_source(query).parse()

        d = ast.to_dict()
        self.assertEqual(d["type"], "SelectQuery")
        self.assertEqual(len(d["projections"]), 2)
        self.assertEqual(d["from_table"]["name"], "students")
        self.assertEqual(d["where"]["operator"], "AND")
        self.assertEqual(len(d["order_by"]), 1)
        self.assertEqual(d["order_by"][0]["direction"], "DESC")

        tree_str = ast.pretty_tree()
        self.assertIn("SelectQuery", tree_str)
        self.assertIn("Projections:", tree_str)
        self.assertIn("students", tree_str)

    # -------------------------------------------------------------------------
    # Negative Syntax Tests (Diagnostics Verification)
    # -------------------------------------------------------------------------

    def test_empty_query_error(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("").parse()
        self.assertIn("Unexpected empty query", str(ctx.exception))

    def test_missing_select_error(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("id FROM users;").parse()
        self.assertIn("Expected 'SELECT' keyword", str(ctx.exception))

    def test_clause_out_of_order_from_first(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("FROM users SELECT id;").parse()
        self.assertIn("Misplaced clause 'FROM'", str(ctx.exception))

    def test_clause_out_of_order_where_before_from(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id WHERE age > 18 FROM users;").parse()
        self.assertIn("Expected 'FROM' clause", str(ctx.exception))

    def test_clause_out_of_order_where_after_order_by(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id FROM users ORDER BY id WHERE age > 18;").parse()
        self.assertIn("Clause out of order: 'WHERE' cannot appear after 'ORDER BY'", str(ctx.exception))

    def test_missing_table_name(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id FROM;").parse()
        self.assertIn("Expected table name identifier", str(ctx.exception))

    def test_trailing_comma_in_projection(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id, name, FROM users;").parse()
        self.assertIn("Trailing comma in SELECT projection list", str(ctx.exception))

    def test_incomplete_where_condition(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id FROM users WHERE age >=;").parse()
        self.assertIn("Expected column identifier or literal constant", str(ctx.exception))

    def test_missing_comparison_operator(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id FROM users WHERE age 18;").parse()
        self.assertIn("Expected relational comparison operator", str(ctx.exception))

    def test_unexpected_trailing_tokens(self):
        with self.assertRaises(SyntaxError) as ctx:
            Parser.from_source("SELECT id FROM users; EXTRA GARBAGE").parse()
        self.assertIn("Unexpected trailing tokens", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
