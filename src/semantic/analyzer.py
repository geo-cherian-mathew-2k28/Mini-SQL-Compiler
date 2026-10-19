"""
Semantic Analyzer for the Mini SQL Compiler.
Validates Context-Free AST representations against the Schema Symbol Table catalog.
Implements Visitor Pattern checks for table existence, column resolution, and type safety.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from src.ast.nodes import (
    ASTNode,
    SelectQuery,
    Wildcard,
    Identifier,
    Literal,
    BinaryExpr,
    OrderByItem,
)
from src.semantic.schema import SchemaCatalog, TableDef, get_default_catalog


@dataclass
class SemanticError:
    """Represents a semantic violation detected during semantic analysis."""
    message: str
    code: str  # e.g., 'TABLE_NOT_FOUND', 'COLUMN_NOT_FOUND', 'TYPE_MISMATCH'

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": "SemanticError",
            "code": self.code,
            "message": self.message,
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


@dataclass
class SemanticReport:
    """Consolidated outcome of semantic analysis."""
    is_valid: bool
    errors: List[SemanticError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    resolved_table: Optional[str] = None
    resolved_columns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
            "resolved_table": self.resolved_table,
            "resolved_columns": self.resolved_columns,
        }


class SemanticAnalyzer:
    """
    Semantic Analyzer performing contextual validation on the AST.
    """

    def __init__(self, catalog: Optional[SchemaCatalog] = None):
        self.catalog: SchemaCatalog = catalog if catalog is not None else get_default_catalog()

    def analyze(self, ast: SelectQuery) -> SemanticReport:
        """Runs all semantic checks on the parsed AST."""
        errors: List[SemanticError] = []
        warnings: List[str] = []
        resolved_cols: List[str] = []

        table_name = ast.from_table.name
        table_def = self.catalog.get_table(table_name)

        # 1. Table Existence Check
        if table_def is None:
            available_tables = ", ".join(f"'{t.name}'" for t in self.catalog.get_all_tables())
            errors.append(
                SemanticError(
                    message=f"Table '{table_name}' does not exist in schema catalog. Available tables: [{available_tables}].",
                    code="TABLE_NOT_FOUND",
                )
            )
            # Cannot proceed with column checks if table does not exist
            return SemanticReport(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                resolved_table=None,
                resolved_columns=[],
            )

        # 2. Projection Columns Resolution
        seen_projections = set()
        for proj in ast.projections:
            if isinstance(proj, Wildcard):
                # Wildcard expands into all catalog columns for the table
                for col in table_def.get_column_names():
                    resolved_cols.append(col)
            elif isinstance(proj, Identifier):
                col_name = proj.name
                if not table_def.has_column(col_name):
                    avail_cols = ", ".join(f"'{c}'" for c in table_def.get_column_names())
                    errors.append(
                        SemanticError(
                            message=f"Column '{col_name}' does not exist in table '{table_name}'. Available columns: [{avail_cols}].",
                            code="COLUMN_NOT_FOUND",
                        )
                    )
                else:
                    resolved_cols.append(col_name)
                    if col_name.lower() in seen_projections:
                        warnings.append(f"Duplicate projection of column '{col_name}' in SELECT list.")
                    seen_projections.add(col_name.lower())

        # 3. Filter Conditions Resolution (WHERE Clause)
        if ast.where:
            self._validate_condition_node(ast.where, table_def, errors)

        # 4. Sorting Specifications Resolution (ORDER BY Clause)
        if ast.order_by:
            for item in ast.order_by:
                col_name = item.column.name
                if not table_def.has_column(col_name):
                    avail_cols = ", ".join(f"'{c}'" for c in table_def.get_column_names())
                    errors.append(
                        SemanticError(
                            message=f"ORDER BY column '{col_name}' does not exist in table '{table_name}'. Available columns: [{avail_cols}].",
                            code="COLUMN_NOT_FOUND",
                        )
                    )

        is_valid = len(errors) == 0
        return SemanticReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            resolved_table=table_def.name,
            resolved_columns=resolved_cols,
        )

    def _validate_condition_node(
        self, node: ASTNode, table_def: TableDef, errors: List[SemanticError]
    ) -> None:
        """Recursively checks column references and operand type compatibility."""
        if not isinstance(node, BinaryExpr):
            return

        # Logical Conjunction/Disjunction (AND / OR)
        if node.operator in ("AND", "OR"):
            self._validate_condition_node(node.left, table_def, errors)
            self._validate_condition_node(node.right, table_def, errors)
            return

        # Relational Comparison Operator (=, !=, <, <=, >, >=)
        left = node.left
        right = node.right

        left_type: Optional[str] = None
        left_desc: str = ""

        # Validate Left Operand
        if isinstance(left, Identifier):
            if not table_def.has_column(left.name):
                avail_cols = ", ".join(f"'{c}'" for c in table_def.get_column_names())
                errors.append(
                    SemanticError(
                        message=f"WHERE column '{left.name}' does not exist in table '{table_def.name}'. Available: [{avail_cols}].",
                        code="COLUMN_NOT_FOUND",
                    )
                )
            else:
                left_type = table_def.get_column(left.name).data_type
                left_desc = f"column '{left.name}' ({left_type})"
        elif isinstance(left, Literal):
            left_type = left.literal_type
            left_desc = f"literal {left.value!r} ({left_type})"

        # Validate Right Operand
        right_type: Optional[str] = None
        right_desc: str = ""

        if isinstance(right, Identifier):
            if not table_def.has_column(right.name):
                avail_cols = ", ".join(f"'{c}'" for c in table_def.get_column_names())
                errors.append(
                    SemanticError(
                        message=f"WHERE column '{right.name}' does not exist in table '{table_def.name}'. Available: [{avail_cols}].",
                        code="COLUMN_NOT_FOUND",
                    )
                )
            else:
                right_type = table_def.get_column(right.name).data_type
                right_desc = f"column '{right.name}' ({right_type})"
        elif isinstance(right, Literal):
            right_type = right.literal_type
            right_desc = f"literal {right.value!r} ({right_type})"

        # Type Compatibility Check
        if left_type and right_type:
            numeric_types = {"INTEGER", "FLOAT"}
            is_left_num = left_type in numeric_types
            is_right_num = right_type in numeric_types

            # Incompatible if one side is numeric and the other is string
            if is_left_num != is_right_num:
                errors.append(
                    SemanticError(
                        message=f"Type mismatch in comparison '{node.operator}': Cannot compare {left_desc} with {right_desc}.",
                        code="TYPE_MISMATCH",
                    )
                )
