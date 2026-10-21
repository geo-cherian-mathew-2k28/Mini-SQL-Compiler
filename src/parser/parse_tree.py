"""
Concrete Parse Tree (CST) and Derivation Tree Node definitions.
Represents the exact grammatical derivation tree according to Context-Free Grammar G'.
Unlike Abstract Syntax Trees, Parse Trees retain all non-terminals, terminal tokens,
keywords, commas, parentheses, and punctuation.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field


@dataclass
class ParseTreeNode:
    """
    Node in a Concrete Parse Tree (CST).
    Can represent either a Non-Terminal symbol (e.g., <Query>, <SelectClause>)
    or a Terminal symbol (Token, e.g., 'SELECT', IDENTIFIER(name), ';').
    """
    symbol: str  # Non-terminal like '<Query>', or terminal like 'SELECT', 'IDENTIFIER'
    is_terminal: bool = False
    lexeme: Optional[str] = None
    children: List["ParseTreeNode"] = field(default_factory=list)

    def add_child(self, child: "ParseTreeNode") -> "ParseTreeNode":
        self.children.append(child)
        return child

    def add_terminal(self, symbol: str, lexeme: str) -> "ParseTreeNode":
        t_node = ParseTreeNode(symbol=symbol, is_terminal=True, lexeme=lexeme)
        self.children.append(t_node)
        return t_node

    def to_dict(self) -> Dict[str, Any]:
        """Convert parse tree to dictionary for JSON serialization & Web rendering."""
        res: Dict[str, Any] = {
            "symbol": self.symbol,
            "is_terminal": self.is_terminal,
        }
        if self.lexeme is not None:
            res["lexeme"] = self.lexeme
        if self.children:
            res["children"] = [child.to_dict() for child in self.children]
        return res

    def pretty_tree(self, indent: int = 0) -> str:
        """Render ASCII representation of the Concrete Parse Tree."""
        pad = "  " * indent
        if self.is_terminal:
            val_str = f" : '{self.lexeme}'" if self.lexeme else ""
            return f"{pad}|-- Terminal({self.symbol}){val_str}\n"

        res = f"{pad}{self.symbol}\n"
        for i, child in enumerate(self.children):
            res += child.pretty_tree(indent + 1)
        return res
