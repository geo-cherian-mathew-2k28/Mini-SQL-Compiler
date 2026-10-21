"""
Hand-written Recursive Descent Syntax Analyzer (Parser) for Mini SQL.
Implements the transformed LL(1) Context-Free Grammar G'.
Constructs BOTH:
1. The Concrete Parse Tree (CST) retaining all non-terminals, terminals, and grammar derivations.
2. The Abstract Syntax Tree (AST) for semantic validation.
"""

from typing import List, Optional, Tuple, Union
from src.lexer.tokens import Token, TokenType
from src.lexer.lexer import Lexer, LexicalError
from src.parser.parse_tree import ParseTreeNode
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
    Top-down recursive descent parser that validates query syntax according to G'.
    Constructs both the Concrete Parse Tree (CST) and the Abstract Syntax Tree (AST).
    Guarantees strict clause order, operator precedence, and detailed diagnostic reporting.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens: List[Token] = tokens
        self.cursor: int = 0
        self.parse_tree_root: Optional[ParseTreeNode] = None

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
        if tok.type != token_type:
            ctx = f" ({context_msg})" if context_msg else ""
            exp = token_type.name
            fnd = tok.lexeme if tok.lexeme else tok.type.name
            raise SyntaxError(
                message=f"Expected '{exp}'{ctx}, but found '{fnd}'",
                line=tok.line,
                column=tok.column,
                expected=exp,
                found=fnd,
            )
        return self._advance()

    # -------------------------------------------------------------------------
    # Core Recursive Descent Parsing Routines (Building AST & Parse Tree)
    # -------------------------------------------------------------------------

    def parse(self) -> SelectQuery:
        """Entry point returning AST (maintaining backwards compatibility)."""
        ast, parse_tree = self.parse_with_tree()
        self.parse_tree_root = parse_tree
        return ast

    def parse_with_tree(self) -> Tuple[SelectQuery, ParseTreeNode]:
        """
        Entry point: Parses query and returns (SelectQuery AST, ParseTreeNode CST).
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

        if tok.type in (TokenType.FROM, TokenType.WHERE, TokenType.ORDER):
            raise SyntaxError(
                message=f"Misplaced clause '{tok.lexeme.upper()}'. Query must begin with 'SELECT'.",
                line=tok.line,
                column=tok.column,
                expected="SELECT",
                found=tok.lexeme,
            )

        query_cst = ParseTreeNode(symbol="<Query>")

        # 1. SELECT clause
        projections, select_cst = self._parse_select_clause()
        query_cst.add_child(select_cst)

        # 2. FROM clause
        from_table, from_cst = self._parse_from_clause()
        query_cst.add_child(from_cst)

        # 3. Optional WHERE clause
        where_cond: Optional[ASTNode] = None
        where_cst = ParseTreeNode(symbol="<OptWhereClause>")
        if self._peek().type == TokenType.WHERE:
            where_cond, inner_where_cst = self._parse_where_clause()
            where_cst.add_child(inner_where_cst)
        else:
            where_cst.add_terminal(symbol="EPSILON", lexeme="EPSILON")
        query_cst.add_child(where_cst)

        # 4. Optional ORDER BY clause
        order_by_items: Optional[List[OrderByItem]] = None
        order_cst = ParseTreeNode(symbol="<OptOrderByClause>")
        if self._peek().type == TokenType.ORDER:
            order_by_items, inner_order_cst = self._parse_order_by_clause()
            order_cst.add_child(inner_order_cst)
        else:
            order_cst.add_terminal(symbol="EPSILON", lexeme="EPSILON")
        query_cst.add_child(order_cst)

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
        semi_cst = ParseTreeNode(symbol="<OptSemicolon>")
        if self._peek().type == TokenType.SEMICOLON:
            semi_tok = self._advance()
            semi_cst.add_terminal(symbol="SEMICOLON", lexeme=semi_tok.lexeme)
        else:
            semi_cst.add_terminal(symbol="EPSILON", lexeme="EPSILON")
        query_cst.add_child(semi_cst)

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

        ast = SelectQuery(
            projections=projections,
            from_table=from_table,
            where=where_cond,
            order_by=order_by_items,
        )
        self.parse_tree_root = query_cst
        return ast, query_cst

    def _parse_select_clause(self) -> Tuple[List[ASTNode], ParseTreeNode]:
        """Parses: 'SELECT' ( '*' | <ColumnList> )"""
        cst = ParseTreeNode(symbol="<SelectClause>")
        sel_tok = self._expect(TokenType.SELECT, "statement initiation")
        cst.add_terminal(symbol="SELECT", lexeme=sel_tok.lexeme)

        select_list_cst = ParseTreeNode(symbol="<SelectList>")
        projections: List[ASTNode] = []

        # Wildcard: '*'
        if self._peek().type == TokenType.ASTERISK:
            star_tok = self._advance()
            select_list_cst.add_terminal(symbol="ASTERISK", lexeme=star_tok.lexeme)
            cst.add_child(select_list_cst)
            projections.append(Wildcard())
            return projections, cst

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

        col_list_cst = ParseTreeNode(symbol="<ColumnList>")
        col_tok = self._advance()
        col_list_cst.add_terminal(symbol="IDENTIFIER", lexeme=col_tok.value)
        projections.append(Identifier(name=col_tok.value))

        curr_tail = col_list_cst
        while self._peek().type == TokenType.COMMA:
            comma_tok = self._advance()
            tail_cst = ParseTreeNode(symbol="<ColumnListTail>")
            tail_cst.add_terminal(symbol="COMMA", lexeme=comma_tok.lexeme)

            next_tok = self._peek()
            if next_tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    message=f"Trailing comma in SELECT projection list. Expected column identifier, found '{next_tok.lexeme or next_tok.type.name}'.",
                    line=next_tok.line,
                    column=next_tok.column,
                    expected="IDENTIFIER",
                    found=next_tok.lexeme or next_tok.type.name,
                )
            next_col = self._advance()
            tail_cst.add_terminal(symbol="IDENTIFIER", lexeme=next_col.value)
            projections.append(Identifier(name=next_col.value))

            curr_tail.add_child(tail_cst)
            curr_tail = tail_cst

        # Add epsilon terminator to tail
        eps_tail = ParseTreeNode(symbol="<ColumnListTail>")
        eps_tail.add_terminal(symbol="EPSILON", lexeme="EPSILON")
        curr_tail.add_child(eps_tail)

        select_list_cst.add_child(col_list_cst)
        cst.add_child(select_list_cst)
        return projections, cst

    def _parse_from_clause(self) -> Tuple[Table, ParseTreeNode]:
        """Parses: 'FROM' IDENTIFIER"""
        cst = ParseTreeNode(symbol="<FromClause>")
        tok = self._peek()
        if tok.type != TokenType.FROM:
            raise SyntaxError(
                message=f"Expected 'FROM' clause following column projections, but found '{tok.lexeme or tok.type.name}'.",
                line=tok.line,
                column=tok.column,
                expected="FROM",
                found=tok.lexeme or tok.type.name,
            )
        from_tok = self._advance()
        cst.add_terminal(symbol="FROM", lexeme=from_tok.lexeme)

        table_tok = self._peek()
        if table_tok.type != TokenType.IDENTIFIER:
            raise SyntaxError(
                message=f"Expected table name identifier after 'FROM', but found '{table_tok.lexeme or table_tok.type.name}'.",
                line=table_tok.line,
                column=table_tok.column,
                expected="IDENTIFIER",
                found=table_tok.lexeme or table_tok.type.name,
            )
        tbl = self._advance()
        cst.add_terminal(symbol="IDENTIFIER", lexeme=tbl.value)
        return Table(name=tbl.value), cst

    def _parse_where_clause(self) -> Tuple[ASTNode, ParseTreeNode]:
        """Parses: 'WHERE' <OrExpr>"""
        cst = ParseTreeNode(symbol="<WhereClause>")
        where_tok = self._expect(TokenType.WHERE, "filtering clause")
        cst.add_terminal(symbol="WHERE", lexeme=where_tok.lexeme)

        expr_ast, expr_cst = self._parse_or_expr()
        cst.add_child(expr_cst)
        return expr_ast, cst

    def _parse_or_expr(self) -> Tuple[ASTNode, ParseTreeNode]:
        """Parses: <AndExpr> ( 'OR' <AndExpr> )*"""
        cst = ParseTreeNode(symbol="<OrExpr>")
        left_ast, left_cst = self._parse_and_expr()
        cst.add_child(left_cst)

        while self._peek().type == TokenType.OR:
            or_tok = self._advance()
            or_node = ParseTreeNode(symbol="<OrTail>")
            or_node.add_terminal(symbol="OR", lexeme=or_tok.lexeme)

            right_ast, right_cst = self._parse_and_expr()
            or_node.add_child(right_cst)
            cst.add_child(or_node)

            left_ast = BinaryExpr(operator="OR", left=left_ast, right=right_ast)

        return left_ast, cst

    def _parse_and_expr(self) -> Tuple[ASTNode, ParseTreeNode]:
        """Parses: <ComparisonExpr> ( 'AND' <ComparisonExpr> )*"""
        cst = ParseTreeNode(symbol="<AndExpr>")
        left_ast, left_cst = self._parse_comparison_expr()
        cst.add_child(left_cst)

        while self._peek().type == TokenType.AND:
            and_tok = self._advance()
            and_node = ParseTreeNode(symbol="<AndTail>")
            and_node.add_terminal(symbol="AND", lexeme=and_tok.lexeme)

            right_ast, right_cst = self._parse_comparison_expr()
            and_node.add_child(right_cst)
            cst.add_child(and_node)

            left_ast = BinaryExpr(operator="AND", left=left_ast, right=right_ast)

        return left_ast, cst

    def _parse_comparison_expr(self) -> Tuple[ASTNode, ParseTreeNode]:
        """Parses: '(' <OrExpr> ')' | <Expression> <RelOp> <Expression>"""
        cst = ParseTreeNode(symbol="<ComparisonExpr>")

        if self._peek().type == TokenType.LPAREN:
            lparen = self._advance()
            cst.add_terminal(symbol="LPAREN", lexeme=lparen.lexeme)

            inner_ast, inner_cst = self._parse_or_expr()
            cst.add_child(inner_cst)

            rparen = self._expect(TokenType.RPAREN, "closing parenthesis for condition grouping")
            cst.add_terminal(symbol="RPAREN", lexeme=rparen.lexeme)
            return inner_ast, cst

        left_ast, left_cst = self._parse_expression()
        cst.add_child(left_cst)

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
        rel_cst = ParseTreeNode(symbol="<RelOp>")
        rel_cst.add_terminal(symbol="OPERATOR", lexeme=op_tok.lexeme)
        cst.add_child(rel_cst)

        # Normalize <> to !=
        op_str = "!=" if op_tok.lexeme == "<>" else op_tok.lexeme

        right_ast, right_cst = self._parse_expression()
        cst.add_child(right_cst)

        return BinaryExpr(operator=op_str, left=left_ast, right=right_ast), cst

    def _parse_expression(self) -> Tuple[ASTNode, ParseTreeNode]:
        """Parses: IDENTIFIER | INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL"""
        cst = ParseTreeNode(symbol="<Expression>")
        tok = self._peek()

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            cst.add_terminal(symbol="IDENTIFIER", lexeme=tok.value)
            return Identifier(name=tok.value), cst

        if tok.type == TokenType.INT_LITERAL:
            self._advance()
            cst.add_terminal(symbol="INT_LITERAL", lexeme=str(tok.value))
            return Literal(value=tok.value, literal_type="INTEGER"), cst

        if tok.type == TokenType.FLOAT_LITERAL:
            self._advance()
            cst.add_terminal(symbol="FLOAT_LITERAL", lexeme=str(tok.value))
            return Literal(value=tok.value, literal_type="FLOAT"), cst

        if tok.type == TokenType.STRING_LITERAL:
            self._advance()
            cst.add_terminal(symbol="STRING_LITERAL", lexeme=f"'{tok.value}'")
            return Literal(value=tok.value, literal_type="STRING"), cst

        raise SyntaxError(
            message=f"Expected column identifier or literal constant, found '{tok.lexeme or tok.type.name}'.",
            line=tok.line,
            column=tok.column,
            expected="IDENTIFIER or LITERAL",
            found=tok.lexeme or tok.type.name,
        )

    def _parse_order_by_clause(self) -> Tuple[List[OrderByItem], ParseTreeNode]:
        """Parses: 'ORDER' 'BY' <OrderByItem> ( ',' <OrderByItem> )*"""
        cst = ParseTreeNode(symbol="<OrderByClause>")
        order_tok = self._expect(TokenType.ORDER, "sorting clause")
        cst.add_terminal(symbol="ORDER", lexeme=order_tok.lexeme)

        by_tok = self._expect(TokenType.BY, "'BY' keyword following 'ORDER'")
        cst.add_terminal(symbol="BY", lexeme=by_tok.lexeme)

        order_list_cst = ParseTreeNode(symbol="<OrderByList>")
        items: List[OrderByItem] = []

        def parse_single_item() -> Tuple[OrderByItem, ParseTreeNode]:
            item_cst = ParseTreeNode(symbol="<OrderByItem>")
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
            item_cst.add_terminal(symbol="IDENTIFIER", lexeme=col_tok.value)
            col = Identifier(name=col_tok.value)

            direction = "ASC"
            dir_cst = ParseTreeNode(symbol="<Direction>")
            if self._peek().type == TokenType.DESC:
                d_tok = self._advance()
                direction = "DESC"
                dir_cst.add_terminal(symbol="DESC", lexeme=d_tok.lexeme)
            elif self._peek().type == TokenType.ASC:
                d_tok = self._advance()
                direction = "ASC"
                dir_cst.add_terminal(symbol="ASC", lexeme=d_tok.lexeme)
            else:
                dir_cst.add_terminal(symbol="EPSILON", lexeme="EPSILON (default ASC)")

            item_cst.add_child(dir_cst)
            return OrderByItem(column=col, direction=direction), item_cst

        first_item, first_cst = parse_single_item()
        items.append(first_item)
        order_list_cst.add_child(first_cst)

        while self._peek().type == TokenType.COMMA:
            comma_tok = self._advance()
            comma_node = ParseTreeNode(symbol="COMMA", is_terminal=True, lexeme=comma_tok.lexeme)
            order_list_cst.add_child(comma_node)

            next_tok = self._peek()
            if next_tok.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    message=f"Trailing comma in ORDER BY list. Expected column identifier, found '{next_tok.lexeme or next_tok.type.name}'.",
                    line=next_tok.line,
                    column=next_tok.column,
                    expected="IDENTIFIER",
                    found=next_tok.lexeme or next_tok.type.name,
                )
            next_item, next_cst = parse_single_item()
            items.append(next_item)
            order_list_cst.add_child(next_cst)

        cst.add_child(order_list_cst)
        return items, cst
