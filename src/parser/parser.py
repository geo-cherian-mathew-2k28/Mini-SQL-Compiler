"""
Hand-written Recursive Descent Syntax Analyzer (Parser) for Mini SQL.
Implements the transformed LL(1) Context-Free Grammar G' and builds the AST.
"""

from typing import List, Optional, Union
from src.lexer.tokens import Token, TokenType
from src.lexer.lexer import Lexer, LexicalError
from src.ast.nodes import (
    ASTNode,
    SelectQuery,
    Wildcard,
    Identifier,
    Table,
    Literal,
    BinaryExpr,
    OrderByItem,
)


class SyntaxError(Exception):
    """Exception raised when a query violates Context-Free Grammar syntax rules."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        expected: Optional[str] = None,
        found: Optional[str] = None,
    ):
        full_msg = f"Syntax Error at line {line}, column {column}: {message}"
        super().__init__(full_msg)
        self.message = message
        self.line = line
        self.column = column
        self.expected = expected
        self.found = found

    def to_dict(self):
        return {
            "type": "SyntaxError",
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "expected": self.expected,
            "found": self.found,
        }


RELATIONAL_OPS = {
    TokenType.EQUALS,
    TokenType.NOT_EQUALS,
    TokenType.LESS_THAN,
    TokenType.LESS_EQUALS,
    TokenType.GREATER_THAN,
    TokenType.GREATER_EQUALS,
}


class Parser:
    """
    Top-down recursive descent parser that validates query syntax and builds the AST.
    Guarantees strict clause order, operator precedence, and detailed diagnostic reporting.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.cursor: int = 0

    @classmethod
    def from_source(cls, source: str) -> "Parser":
        """Convenience factory: tokenizes source text and initializes parser."""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        return cls(tokens)

    def _peek(self, offset: int = 0) -> Token:
        target = self.cursor + offset
        if target >= len(self.tokens):
            return self.tokens[-1]  # Return EOF token
        return self.tokens[target]

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _advance(self) -> Token:
        tok = self._peek()
        if tok.type != TokenType.EOF:
            self.cursor += 1
        return tok

    def _match(self, *token_types: TokenType) -> bool:
        if self._peek().type in token_types:
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, context_msg: str = "") -> Token:
        tok = self._peek()
        if tok.type == token_type:
            return self._advance()

        exp_name = token_type.name
        found_name = tok.type.name if tok.type != TokenType.EOF else "EOF"
        found_lexeme = tok.lexeme if tok.lexeme else found_name
        detail = f" ({context_msg})" if context_msg else ""
        msg = f"Expected '{exp_name}'{detail}, but found '{found_lexeme}'"
        raise SyntaxError(
            message=msg,
            line=tok.line,
            column=tok.column,
            expected=exp_name,
            found=found_lexeme,
        )

    # -------------------------------------------------------------------------
    # Core Recursive Descent Parsing Routines
    # -------------------------------------------------------------------------

    def parse(self) -> SelectQuery:
        """
        Entry point: Parses a complete SQL query according to G':
        <Query> ::= <SelectClause> <FromClause> <OptWhereClause> <OptOrderByClause> <OptSemicolon>
        """
        tok = self._peek()

        if tok.type == TokenType.EOF:
            raise SyntaxError(
                message="Unexpected empty query. Statement must start with 'SELECT'.",
                line=tok.line,
                column=tok.column,
                expected="SELECT",
                found="EOF",
            )

        # Detect clause ordering violation at query start
        if tok.type in (TokenType.FROM, TokenType.WHERE, TokenType.ORDER):
            raise SyntaxError(
                message=f"Misplaced clause '{tok.lexeme.upper()}'. Query must begin with 'SELECT'.",
                line=tok.line,
                column=tok.column,
                expected="SELECT",
                found=tok.lexeme,
            )

        # 1. SELECT clause
        projections = self._parse_select_clause()

        # 2. FROM clause
        from_table = self._parse_from_clause()

        # 3. Optional WHERE clause
        where_cond: Optional[ASTNode] = None
        if self._peek().type == TokenType.WHERE:
            where_cond = self._parse_where_clause()

        # 4. Optional ORDER BY clause
        order_by_items: Optional[List[OrderByItem]] = None
        if self._peek().type == TokenType.ORDER:
            order_by_items = self._parse_order_by_clause()

        # Check for out-of-order clauses after ORDER BY
        if self._peek().type == TokenType.WHERE:
            tok = self._peek()
            raise SyntaxError(
                message="Clause out of order: 'WHERE' cannot appear after 'ORDER BY'.",
                line=tok.line,
                column=tok.column,
                expected="SEMICOLON or EOF",
                found="WHERE",
            )

        # 5. Optional Semicolon
        self._match(TokenType.SEMICOLON)

        # Ensure no trailing illegal tokens
        if not self._check(TokenType.EOF):
            tok = self._peek()
            raise SyntaxError(
                message=f"Unexpected trailing tokens after statement terminator: '{tok.lexeme}'.",
                line=tok.line,
                column=tok.column,
                expected="EOF",
                found=tok.lexeme,
            )

        return SelectQuery(
            projections=projections,
            from_table=from_table,
            where=where_cond,
            order_by=order_by_items,
        )

    def _parse_select_clause(self) -> List[ASTNode]:
        """Parses: 'SELECT' ( '*' | <ColumnList> )"""
        self._expect(TokenType.SELECT, "statement initiation")

        projections: List[ASTNode] = []

        # Wildcard: '*'
        if self._match(TokenType.ASTERISK):
            projections.append(Wildcard())
            return projections

        # Non-empty comma-separated list of column identifiers
        tok = self._peek()
        if tok.type != TokenType.IDENTIFIER:
            raise SyntaxError(
                message=f"Expected column identifier or '*' after 'SELECT', found '{tok.lexeme or tok.type.name}'.",
                line=tok.line,
                column=tok.column,
                expected="IDENTIFIER or '*'",
                found=tok.lexeme or tok.type.name,
            )

        col_tok = self._advance()
        projections.append(Identifier(name=col_tok.value))

        while self._match(TokenType.COMMA):
            next_tok = self._peek()
            if next_tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    message=f"Trailing comma in SELECT projection list. Expected column identifier, found '{next_tok.lexeme or next_tok.type.name}'.",
                    line=next_tok.line,
                    column=next_tok.column,
                    expected="IDENTIFIER",
                    found=next_tok.lexeme or next_tok.type.name,
                )
            projections.append(Identifier(name=self._advance().value))

        return projections

    def _parse_from_clause(self) -> Table:
        """Parses: 'FROM' IDENTIFIER"""
        tok = self._peek()
        if tok.type != TokenType.FROM:
            raise SyntaxError(
                message=f"Expected 'FROM' clause following column projections, but found '{tok.lexeme or tok.type.name}'.",
                line=tok.line,
                column=tok.column,
                expected="FROM",
                found=tok.lexeme or tok.type.name,
            )
        self._advance()

        table_tok = self._peek()
        if table_tok.type != TokenType.IDENTIFIER:
            raise SyntaxError(
                message=f"Expected table name identifier after 'FROM', but found '{table_tok.lexeme or table_tok.type.name}'.",
                line=table_tok.line,
                column=table_tok.column,
                expected="IDENTIFIER",
                found=table_tok.lexeme or table_tok.type.name,
            )

        self._advance()
        return Table(name=table_tok.value)

    def _parse_where_clause(self) -> ASTNode:
        """Parses: 'WHERE' <OrExpr>"""
        self._expect(TokenType.WHERE, "filtering clause")
        return self._parse_or_expr()

    def _parse_or_expr(self) -> ASTNode:
        """Parses: <AndExpr> ( 'OR' <AndExpr> )*"""
        left = self._parse_and_expr()

        while self._match(TokenType.OR):
            op = "OR"
            right = self._parse_and_expr()
            left = BinaryExpr(operator=op, left=left, right=right)

        return left

    def _parse_and_expr(self) -> ASTNode:
        """Parses: <ComparisonExpr> ( 'AND' <ComparisonExpr> )*"""
        left = self._parse_comparison_expr()

        while self._match(TokenType.AND):
            op = "AND"
            right = self._parse_comparison_expr()
            left = BinaryExpr(operator=op, left=left, right=right)

        return left

    def _parse_comparison_expr(self) -> ASTNode:
        """Parses: '(' <OrExpr> ')' | <Expression> <RelOp> <Expression>"""
        if self._match(TokenType.LPAREN):
            expr = self._parse_or_expr()
            self._expect(TokenType.RPAREN, "closing parenthesis for condition grouping")
            return expr

        left = self._parse_expression()

        op_tok = self._peek()
        if op_tok.type not in RELATIONAL_OPS:
            raise SyntaxError(
                message=f"Expected relational comparison operator (=, !=, <, >, <=, >=), found '{op_tok.lexeme or op_tok.type.name}'.",
                line=op_tok.line,
                column=op_tok.column,
                expected="RELATIONAL_OPERATOR",
                found=op_tok.lexeme or op_tok.type.name,
            )
        self._advance()
        # Normalize <> to !=
        op_str = "!=" if op_tok.lexeme == "<>" else op_tok.lexeme

        right = self._parse_expression()
        return BinaryExpr(operator=op_str, left=left, right=right)

    def _parse_expression(self) -> ASTNode:
        """Parses: IDENTIFIER | INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL"""
        tok = self._peek()

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Identifier(name=tok.value)

        if tok.type == TokenType.INT_LITERAL:
            self._advance()
            return Literal(value=tok.value, literal_type="INTEGER")

        if tok.type == TokenType.FLOAT_LITERAL:
            self._advance()
            return Literal(value=tok.value, literal_type="FLOAT")

        if tok.type == TokenType.STRING_LITERAL:
            self._advance()
            return Literal(value=tok.value, literal_type="STRING")

        raise SyntaxError(
            message=f"Expected column identifier or literal constant, found '{tok.lexeme or tok.type.name}'.",
            line=tok.line,
            column=tok.column,
            expected="IDENTIFIER or LITERAL",
            found=tok.lexeme or tok.type.name,
        )

    def _parse_order_by_clause(self) -> List[OrderByItem]:
        """Parses: 'ORDER' 'BY' <OrderByItem> ( ',' <OrderByItem> )*"""
        self._expect(TokenType.ORDER, "sorting clause")
        self._expect(TokenType.BY, "'BY' keyword following 'ORDER'")

        items: List[OrderByItem] = []

        def parse_single_item() -> OrderByItem:
            col_tok = self._peek()
            if col_tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    message=f"Expected column name for ORDER BY, found '{col_tok.lexeme or col_tok.type.name}'.",
                    line=col_tok.line,
                    column=col_tok.column,
                    expected="IDENTIFIER",
                    found=col_tok.lexeme or col_tok.type.name,
                )
            self._advance()
            col = Identifier(name=col_tok.value)

            direction = "ASC"
            if self._match(TokenType.DESC):
                direction = "DESC"
            elif self._match(TokenType.ASC):
                direction = "ASC"

            return OrderByItem(column=col, direction=direction)

        items.append(parse_single_item())

        while self._match(TokenType.COMMA):
            next_tok = self._peek()
            if next_tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    message=f"Trailing comma in ORDER BY list. Expected column identifier, found '{next_tok.lexeme or next_tok.type.name}'.",
                    line=next_tok.line,
                    column=next_tok.column,
                    expected="IDENTIFIER",
                    found=next_tok.lexeme or next_tok.type.name,
                )
            items.append(parse_single_item())

        return items
