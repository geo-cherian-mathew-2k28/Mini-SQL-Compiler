"""
Token definitions and classifications for the Mini SQL Compiler.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict


class TokenType(Enum):
    # SQL Keywords (Case-insensitive)
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    ORDER = auto()
    BY = auto()
    ASC = auto()
    DESC = auto()
    AND = auto()
    OR = auto()

    # Identifiers & Literals
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()

    # Relational Operators
    EQUALS = auto()            # =
    NOT_EQUALS = auto()        # != or <>
    LESS_THAN = auto()         # <
    LESS_EQUALS = auto()       # <=
    GREATER_THAN = auto()      # >
    GREATER_EQUALS = auto()    # >=

    # Punctuation & Delimiters
    ASTERISK = auto()          # * (Projection Wildcard)
    COMMA = auto()             # ,
    SEMICOLON = auto()         # ;
    LPAREN = auto()            # (
    RPAREN = auto()            # )

    # End of Input
    EOF = auto()


# Keyword lookup table (Normalized to uppercase)
KEYWORDS: Dict[str, TokenType] = {
    "SELECT": TokenType.SELECT,
    "FROM": TokenType.FROM,
    "WHERE": TokenType.WHERE,
    "ORDER": TokenType.ORDER,
    "BY": TokenType.BY,
    "ASC": TokenType.ASC,
    "DESC": TokenType.DESC,
    "AND": TokenType.AND,
    "OR": TokenType.OR,
}


@dataclass(frozen=True)
class Token:
    """
    Represents a lexical token produced by the Lexical Analyzer.
    
    Attributes:
        type: The categorical classification (TokenType).
        lexeme: The exact raw substring from the source query.
        value: The parsed semantic value (e.g., int, float, stripped string, or identifier name).
        line: 1-indexed line position in the source text.
        column: 1-indexed column position in the source text.
    """
    type: TokenType
    lexeme: str
    value: Any
    line: int
    column: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to JSON-serializable dictionary for web API and visual inspection."""
        return {
            "type": self.type.name,
            "lexeme": self.lexeme,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self) -> str:
        return f"Token({self.type.name}, lexeme={self.lexeme!r}, val={self.value!r}, line={self.line}, col={self.column})"
