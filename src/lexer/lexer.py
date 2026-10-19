"""
Hand-written Lexical Analyzer (Scanner) for the Mini SQL Compiler.
Tokenizes raw SQL text into a stream of Token instances with precise location tracking.
"""

from typing import List, Optional
from src.lexer.tokens import Token, TokenType, KEYWORDS


class LexicalError(Exception):
    """Exception raised when illegal characters or malformed tokens are encountered."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexical Error at line {line}, column {column}: {message}")
        self.message = message
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "type": "LexicalError",
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }


class Lexer:
    """
    Hand-written lexical scanner implementing deterministic finite state scanning.
    Tracks line and column coordinates for every lexeme to provide rich diagnostics.
    """

    def __init__(self, source: str):
        self.source: str = source
        self.length: int = len(source)
        self.cursor: int = 0
        self.line: int = 1
        self.column: int = 1

    def _peek(self, offset: int = 0) -> str:
        """Lookahead character without advancing the cursor."""
        target = self.cursor + offset
        if target >= self.length:
            return ""
        return self.source[target]

    def _advance(self) -> str:
        """Consume and return the current character, updating coordinates."""
        if self.cursor >= self.length:
            return ""
        char = self.source[self.cursor]
        self.cursor += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _skip_whitespace_and_comments(self) -> None:
        """Skip whitespace and SQL comments (-- single-line and /* multi-line */)."""
        while self.cursor < self.length:
            char = self._peek()

            # Whitespace
            if char in (" ", "\t", "\r", "\n"):
                self._advance()
                continue

            # Single-line comment: -- comment
            if char == "-" and self._peek(1) == "-":
                self._advance()
                self._advance()
                while self.cursor < self.length and self._peek() != "\n":
                    self._advance()
                continue

            # Multi-line comment: /* comment */
            if char == "/" and self._peek(1) == "*":
                start_line = self.line
                start_col = self.column
                self._advance()
                self._advance()
                closed = False
                while self.cursor < self.length:
                    if self._peek() == "*" and self._peek(1) == "/":
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()
                if not closed:
                    raise LexicalError("Unterminated multi-line comment", start_line, start_col)
                continue

            break

    def _scan_identifier_or_keyword(self) -> Token:
        """Scans identifiers and case-insensitive SQL keywords."""
        start_line = self.line
        start_col = self.column
        chars = []

        while self.cursor < self.length:
            c = self._peek()
            if c.isalnum() or c == "_":
                chars.append(self._advance())
            else:
                break

        lexeme = "".join(chars)
        upper_lexeme = lexeme.upper()

        if upper_lexeme in KEYWORDS:
            return Token(
                type=KEYWORDS[upper_lexeme],
                lexeme=lexeme,
                value=upper_lexeme,
                line=start_line,
                column=start_col,
            )
        else:
            return Token(
                type=TokenType.IDENTIFIER,
                lexeme=lexeme,
                value=lexeme,
                line=start_line,
                column=start_col,
            )

    def _scan_number(self) -> Token:
        """Scans integer and floating-point numeric literals."""
        start_line = self.line
        start_col = self.column
        chars = []
        is_float = False

        while self.cursor < self.length and self._peek().isdigit():
            chars.append(self._advance())

        # Check for fractional component
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            chars.append(self._advance())  # Consume '.'
            while self.cursor < self.length and self._peek().isdigit():
                chars.append(self._advance())

        lexeme = "".join(chars)
        value = float(lexeme) if is_float else int(lexeme)
        token_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INT_LITERAL

        return Token(
            type=token_type,
            lexeme=lexeme,
            value=value,
            line=start_line,
            column=start_col,
        )

    def _scan_string(self) -> Token:
        """Scans single-quoted string literals with SQL escaping ('' or \')."""
        start_line = self.line
        start_col = self.column
        chars = []

        # Consume opening single quote
        quote_char = self._advance()
        raw_chars = [quote_char]

        while self.cursor < self.length:
            c = self._peek()

            # SQL escaping: '' inside string
            if c == "'" and self._peek(1) == "'":
                raw_chars.append(self._advance())
                raw_chars.append(self._advance())
                chars.append("'")
                continue

            # Standard backslash escape
            if c == "\\":
                raw_chars.append(self._advance())
                escaped = self._advance()
                raw_chars.append(escaped)
                if escaped == "n":
                    chars.append("\n")
                elif escaped == "t":
                    chars.append("\t")
                elif escaped == "'":
                    chars.append("'")
                elif escaped == "\\":
                    chars.append("\\")
                else:
                    chars.append(escaped)
                continue

            # Closing quote
            if c == "'":
                raw_chars.append(self._advance())
                lexeme = "".join(raw_chars)
                value = "".join(chars)
                return Token(
                    type=TokenType.STRING_LITERAL,
                    lexeme=lexeme,
                    value=value,
                    line=start_line,
                    column=start_col,
                )

            # Regular character
            raw_chars.append(c)
            chars.append(self._advance())

        raise LexicalError("Unterminated string literal", start_line, start_col)

    def next_token(self) -> Token:
        """Retrieves the next token from the input stream."""
        self._skip_whitespace_and_comments()

        if self.cursor >= self.length:
            return Token(
                type=TokenType.EOF,
                lexeme="",
                value=None,
                line=self.line,
                column=self.column,
            )

        start_line = self.line
        start_col = self.column
        char = self._peek()

        # Identifiers and keywords: [a-zA-Z_]
        if char.isalpha() or char == "_":
            return self._scan_identifier_or_keyword()

        # Numeric literals: [0-9]
        if char.isdigit():
            return self._scan_number()

        # String literals: 'string'
        if char == "'":
            return self._scan_string()

        # Relational operators & punctuation
        # != or <>
        if char == "!" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.NOT_EQUALS, "!=", "!=", start_line, start_col)

        if char == "<" and self._peek(1) == ">":
            self._advance()
            self._advance()
            return Token(TokenType.NOT_EQUALS, "<>", "!=", start_line, start_col)

        if char == "<" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.LESS_EQUALS, "<=", "<=", start_line, start_col)

        if char == ">" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.GREATER_EQUALS, ">=", ">=", start_line, start_col)

        if char == "<":
            self._advance()
            return Token(TokenType.LESS_THAN, "<", "<", start_line, start_col)

        if char == ">":
            self._advance()
            return Token(TokenType.GREATER_THAN, ">", ">", start_line, start_col)

        if char == "=":
            self._advance()
            return Token(TokenType.EQUALS, "=", "=", start_line, start_col)

        # Delimiters
        if char == "*":
            self._advance()
            return Token(TokenType.ASTERISK, "*", "*", start_line, start_col)

        if char == ",":
            self._advance()
            return Token(TokenType.COMMA, ",", ",", start_line, start_col)

        if char == ";":
            self._advance()
            return Token(TokenType.SEMICOLON, ";", ";", start_line, start_col)

        if char == "(":
            self._advance()
            return Token(TokenType.LPAREN, "(", "(", start_line, start_col)

        if char == ")":
            self._advance()
            return Token(TokenType.RPAREN, ")", ")", start_line, start_col)

        # Illegal character
        bad_char = self._advance()
        raise LexicalError(f"Unexpected character '{bad_char}'", start_line, start_col)

    def tokenize(self) -> List[Token]:
        """Tokenize entire input string into a list of Tokens, ending with EOF."""
        tokens: List[Token] = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens
