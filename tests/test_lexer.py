"""
Comprehensive unit tests for the Lexical Analyzer (Lexer).
"""

import unittest
from src.lexer.tokens import TokenType
from src.lexer.lexer import Lexer, LexicalError


class TestLexer(unittest.TestCase):

    def test_basic_select_from(self):
        query = "SELECT id, name FROM users;"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        expected = [
            (TokenType.SELECT, "SELECT"),
            (TokenType.IDENTIFIER, "id"),
            (TokenType.COMMA, ","),
            (TokenType.IDENTIFIER, "name"),
            (TokenType.FROM, "FROM"),
            (TokenType.IDENTIFIER, "users"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.EOF, ""),
        ]

        self.assertEqual(len(tokens), len(expected))
        for tok, (exp_type, exp_lexeme) in zip(tokens, expected):
            self.assertEqual(tok.type, exp_type)
            self.assertEqual(tok.lexeme, exp_lexeme)

    def test_wildcard_select(self):
        query = "SELECT * FROM employees"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.SELECT)
        self.assertEqual(tokens[1].type, TokenType.ASTERISK)
        self.assertEqual(tokens[2].type, TokenType.FROM)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[4].type, TokenType.EOF)

    def test_case_insensitivity(self):
        query = "select name from tbl where age >= 18 order by name desc;"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.SELECT)
        self.assertEqual(tokens[2].type, TokenType.FROM)
        self.assertEqual(tokens[4].type, TokenType.WHERE)
        self.assertEqual(tokens[6].type, TokenType.GREATER_EQUALS)
        self.assertEqual(tokens[7].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[7].value, 18)
        self.assertEqual(tokens[8].type, TokenType.ORDER)
        self.assertEqual(tokens[9].type, TokenType.BY)
        self.assertEqual(tokens[11].type, TokenType.DESC)

    def test_all_relational_operators(self):
        query = "= != <> < <= > >="
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        expected_types = [
            TokenType.EQUALS,
            TokenType.NOT_EQUALS,
            TokenType.NOT_EQUALS,
            TokenType.LESS_THAN,
            TokenType.LESS_EQUALS,
            TokenType.GREATER_THAN,
            TokenType.GREATER_EQUALS,
            TokenType.EOF,
        ]

        self.assertEqual([t.type for t in tokens], expected_types)

    def test_numeric_literals(self):
        query = "100 42.5 0 999.001"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[0].value, 100)

        self.assertEqual(tokens[1].type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[1].value, 42.5)

        self.assertEqual(tokens[2].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[2].value, 0)

        self.assertEqual(tokens[3].type, TokenType.FLOAT_LITERAL)
        self.assertEqual(tokens[3].value, 999.001)

    def test_string_literals_and_escapes(self):
        query = "'John Doe' 'O''Reilly' 'line\\nbreak'"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL)
        self.assertEqual(tokens[0].value, "John Doe")

        self.assertEqual(tokens[1].type, TokenType.STRING_LITERAL)
        self.assertEqual(tokens[1].value, "O'Reilly")

        self.assertEqual(tokens[2].type, TokenType.STRING_LITERAL)
        self.assertEqual(tokens[2].value, "line\nbreak")

    def test_line_and_column_tracking(self):
        query = "SELECT\n  id,\n  name\nFROM users;"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        # SELECT at line 1, col 1
        self.assertEqual((tokens[0].line, tokens[0].column), (1, 1))
        # id at line 2, col 3
        self.assertEqual((tokens[1].line, tokens[1].column), (2, 3))
        # , at line 2, col 5
        self.assertEqual((tokens[2].line, tokens[2].column), (2, 5))
        # name at line 3, col 3
        self.assertEqual((tokens[3].line, tokens[3].column), (3, 3))
        # FROM at line 4, col 1
        self.assertEqual((tokens[4].line, tokens[4].column), (4, 1))

    def test_sql_comments_skipping(self):
        query = """
        -- Leading single-line comment
        SELECT id /* in-line multi-line comment */ FROM accounts;
        -- Trailing comment
        """
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[0].type, TokenType.SELECT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].lexeme, "id")
        self.assertEqual(tokens[2].type, TokenType.FROM)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].lexeme, "accounts")
        self.assertEqual(tokens[4].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[5].type, TokenType.EOF)

    def test_parentheses_and_logical_ops(self):
        query = "WHERE (age > 21 AND salary >= 50000) OR department = 'Sales'"
        lexer = Lexer(query)
        tokens = lexer.tokenize()

        types = [t.type for t in tokens]
        self.assertIn(TokenType.LPAREN, types)
        self.assertIn(TokenType.RPAREN, types)
        self.assertIn(TokenType.AND, types)
        self.assertIn(TokenType.OR, types)

    def test_unterminated_string_error(self):
        query = "SELECT id FROM users WHERE name = 'Unclosed string;"
        lexer = Lexer(query)
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Unterminated string literal", str(ctx.exception))

    def test_illegal_character_error(self):
        query = "SELECT id @ FROM users;"
        lexer = Lexer(query)
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Unexpected character '@'", str(ctx.exception))
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, 11)

    def test_unterminated_multiline_comment_error(self):
        query = "SELECT id /* unclosed comment FROM users;"
        lexer = Lexer(query)
        with self.assertRaises(LexicalError) as ctx:
            lexer.tokenize()
        self.assertIn("Unterminated multi-line comment", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
