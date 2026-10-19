"""
Abstract Syntax Tree (AST) node definitions for the Mini SQL Compiler.
Every node supports JSON serialization (to_dict) and hierarchical tree printing (pretty_tree).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class ASTNode(ABC):
    """Abstract base class for all AST nodes."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert AST node to JSON-serializable dictionary."""
        pass

    @abstractmethod
    def pretty_tree(self, indent: int = 0) -> str:
        """Render readable indented tree representation."""
        pass


@dataclass
class Wildcard(ASTNode):
    """Represents the '*' wildcard projection."""

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Wildcard", "value": "*"}

    def pretty_tree(self, indent: int = 0) -> str:
        return "  " * indent + "Wildcard(*)\n"


@dataclass
class Identifier(ASTNode):
    """Represents a column name identifier."""
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Identifier", "name": self.name}

    def pretty_tree(self, indent: int = 0) -> str:
        return "  " * indent + f"Identifier({self.name})\n"


@dataclass
class Table(ASTNode):
    """Represents a table reference in the FROM clause."""
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Table", "name": self.name}

    def pretty_tree(self, indent: int = 0) -> str:
        return "  " * indent + f"Table({self.name})\n"


@dataclass
class Literal(ASTNode):
    """Represents integer, float, or string constants."""
    value: Any
    literal_type: str  # 'INTEGER', 'FLOAT', or 'STRING'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Literal",
            "literal_type": self.literal_type,
            "value": self.value,
        }

    def pretty_tree(self, indent: int = 0) -> str:
        return "  " * indent + f"Literal({self.literal_type}: {self.value!r})\n"


@dataclass
class BinaryExpr(ASTNode):
    """
    Represents binary operations:
    - Logical operators: 'AND', 'OR'
    - Relational comparisons: '=', '!=', '<>', '<', '<=', '>', '>='
    """
    operator: str
    left: ASTNode
    right: ASTNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryExpr",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

    def pretty_tree(self, indent: int = 0) -> str:
        res = "  " * indent + f"BinaryExpr({self.operator})\n"
        res += "  " * (indent + 1) + "├── Left:\n" + self.left.pretty_tree(indent + 2)
        res += "  " * (indent + 1) + "└── Right:\n" + self.right.pretty_tree(indent + 2)
        return res


@dataclass
class OrderByItem(ASTNode):
    """Represents a column sorting specifier with direction (ASC or DESC)."""
    column: Identifier
    direction: str  # 'ASC' or 'DESC'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "OrderByItem",
            "column": self.column.to_dict(),
            "direction": self.direction,
        }

    def pretty_tree(self, indent: int = 0) -> str:
        return "  " * indent + f"OrderByItem(col={self.column.name}, dir={self.direction})\n"


@dataclass
class SelectQuery(ASTNode):
    """
    Root node representing a complete parsed SQL SELECT query.
    Encapsulates: SELECT, FROM, optional WHERE, and optional ORDER BY.
    """
    projections: List[ASTNode]
    from_table: Table
    where: Optional[ASTNode] = None
    order_by: Optional[List[OrderByItem]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "SelectQuery",
            "projections": [p.to_dict() for p in self.projections],
            "from_table": self.from_table.to_dict(),
            "where": self.where.to_dict() if self.where else None,
            "order_by": [o.to_dict() for o in self.order_by] if self.order_by else None,
        }

    def pretty_tree(self, indent: int = 0) -> str:
        pad = "  " * indent
        res = pad + "SelectQuery\n"

        # Projections
        res += pad + "  ├── Projections:\n"
        for p in self.projections:
            res += p.pretty_tree(indent + 2)

        # From
        res += pad + "  ├── From:\n"
        res += self.from_table.pretty_tree(indent + 2)

        # Where
        res += pad + "  ├── Where:\n"
        if self.where:
            res += self.where.pretty_tree(indent + 2)
        else:
            res += pad + "    └── None\n"

        # Order By
        res += pad + "  └── OrderBy:\n"
        if self.order_by:
            for item in self.order_by:
                res += item.pretty_tree(indent + 2)
        else:
            res += pad + "    └── None\n"

        return res
