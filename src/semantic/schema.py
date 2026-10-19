"""
Predefined Schema Symbol Table and Catalog Definitions for Semantic Analysis.
Provides metadata for tables, columns, and data types to validate SQL queries.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ColumnDef:
    """Definition of a single table column in the catalog."""
    name: str
    data_type: str  # 'INTEGER', 'FLOAT', or 'STRING'
    nullable: bool = True

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "data_type": self.data_type,
            "nullable": self.nullable,
        }


@dataclass
class TableDef:
    """Definition of a database table in the catalog."""
    name: str
    columns: Dict[str, ColumnDef] = field(default_factory=dict)

    def has_column(self, col_name: str) -> bool:
        return col_name.lower() in self.columns

    def get_column(self, col_name: str) -> Optional[ColumnDef]:
        return self.columns.get(col_name.lower())

    def get_column_names(self) -> List[str]:
        return [c.name for c in self.columns.values()]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "columns": [c.to_dict() for c in self.columns.values()],
        }


class SchemaCatalog:
    """
    Symbol table repository storing table schemas.
    Used by the Semantic Analyzer to verify tables, columns, and type safety.
    """

    def __init__(self):
        self.tables: Dict[str, TableDef] = {}

    def register_table(self, name: str, columns: List[ColumnDef]) -> None:
        table = TableDef(name=name)
        for col in columns:
            table.columns[col.name.lower()] = col
        self.tables[name.lower()] = table

    def get_table(self, name: str) -> Optional[TableDef]:
        return self.tables.get(name.lower())

    def has_table(self, name: str) -> bool:
        return name.lower() in self.tables

    def get_all_tables(self) -> List[TableDef]:
        return list(self.tables.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tables": {t.name: t.to_dict() for t in self.tables.values()}
        }


def get_default_catalog() -> SchemaCatalog:
    """
    Initializes a standard academic demonstration catalog with realistic tables.
    """
    catalog = SchemaCatalog()

    # Table 1: students
    catalog.register_table(
        "students",
        [
            ColumnDef("id", "INTEGER", nullable=False),
            ColumnDef("name", "STRING", nullable=False),
            ColumnDef("age", "INTEGER", nullable=False),
            ColumnDef("gpa", "FLOAT", nullable=True),
            ColumnDef("department", "STRING", nullable=False),
        ],
    )

    # Table 2: employees
    catalog.register_table(
        "employees",
        [
            ColumnDef("emp_id", "INTEGER", nullable=False),
            ColumnDef("name", "STRING", nullable=False),
            ColumnDef("salary", "FLOAT", nullable=False),
            ColumnDef("department", "STRING", nullable=False),
            ColumnDef("age", "INTEGER", nullable=False),
        ],
    )

    # Table 3: orders
    catalog.register_table(
        "orders",
        [
            ColumnDef("order_id", "INTEGER", nullable=False),
            ColumnDef("customer_id", "INTEGER", nullable=False),
            ColumnDef("amount", "FLOAT", nullable=False),
            ColumnDef("status", "STRING", nullable=False),
            ColumnDef("order_date", "STRING", nullable=False),
        ],
    )

    # Table 4: products
    catalog.register_table(
        "products",
        [
            ColumnDef("product_id", "INTEGER", nullable=False),
            ColumnDef("title", "STRING", nullable=False),
            ColumnDef("price", "FLOAT", nullable=False),
            ColumnDef("stock", "INTEGER", nullable=False),
        ],
    )

    return catalog
