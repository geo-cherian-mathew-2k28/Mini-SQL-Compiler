"""
Master Compiler Orchestrator for Mini SQL.
Connects Lexer -> Parser -> AST -> Semantic Analyzer into a unified pipeline.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.lexer.tokens import Token
from src.lexer.lexer import Lexer, LexicalError
from src.parser.parser import Parser, SyntaxError as SQLSyntaxError
from src.ast.nodes import SelectQuery
from src.semantic.schema import SchemaCatalog, get_default_catalog
from src.semantic.analyzer import SemanticAnalyzer, SemanticReport


@dataclass
class CompilationResult:
    """Consolidated outcome of the entire compiler front-end pipeline."""
    success: bool
    stage_reached: str  # 'LEXED', 'PARSED', 'SEMANTIC_CHECKED', or 'FAILED'
    query: str
    tokens: List[Dict[str, Any]] = field(default_factory=list)
    ast: Optional[Dict[str, Any]] = None
    ast_pretty: Optional[str] = None
    semantic_report: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stage_reached": self.stage_reached,
            "query": self.query,
            "tokens": self.tokens,
            "ast": self.ast,
            "ast_pretty": self.ast_pretty,
            "semantic_report": self.semantic_report,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class MiniSQLCompiler:
    """
    Main Compiler Front-End Driver.
    Orchestrates Lexical, Syntactic, and Semantic analysis stages.
    """

    def __init__(self, catalog: Optional[SchemaCatalog] = None):
        self.catalog: SchemaCatalog = catalog if catalog is not None else get_default_catalog()
        self.semantic_analyzer = SemanticAnalyzer(self.catalog)

    def compile(self, query: str) -> CompilationResult:
        """
        Executes all front-end compiler phases on the provided SQL query.
        Gracefully traps errors at each stage to return actionable diagnostics.
        """
        clean_query = query.strip()
        errors: List[Dict[str, Any]] = []
        warnings: List[str] = []
        token_dicts: List[Dict[str, Any]] = []

        # =====================================================================
        # Phase 1: Lexical Analysis (Scanner)
        # =====================================================================
        lexer = Lexer(clean_query)
        raw_tokens: List[Token] = []

        try:
            raw_tokens = lexer.tokenize()
            token_dicts = [t.to_dict() for t in raw_tokens]
        except LexicalError as le:
            errors.append({
                "stage": "Lexical Analysis",
                "type": "LexicalError",
                "message": le.message,
                "line": le.line,
                "column": le.column,
            })
            return CompilationResult(
                success=False,
                stage_reached="LEXICAL_FAILED",
                query=clean_query,
                tokens=token_dicts,
                errors=errors,
            )

        # =====================================================================
        # Phase 2: Syntax Analysis & AST Construction (Parser)
        # =====================================================================
        parser = Parser(raw_tokens)
        ast: Optional[SelectQuery] = None

        try:
            ast = parser.parse()
        except SQLSyntaxError as se:
            errors.append({
                "stage": "Syntax Analysis",
                "type": "SyntaxError",
                "message": se.message,
                "line": se.line,
                "column": se.column,
                "expected": se.expected,
                "found": se.found,
            })
            return CompilationResult(
                success=False,
                stage_reached="SYNTAX_FAILED",
                query=clean_query,
                tokens=token_dicts,
                errors=errors,
            )

        ast_dict = ast.to_dict()
        ast_pretty = ast.pretty_tree()

        # =====================================================================
        # Phase 3: Semantic Analysis (Contextual Type & Symbol Validation)
        # =====================================================================
        report = self.semantic_analyzer.analyze(ast)

        if not report.is_valid:
            for sem_err in report.errors:
                errors.append({
                    "stage": "Semantic Analysis",
                    "type": "SemanticError",
                    "code": sem_err.code,
                    "message": sem_err.message,
                    "line": None,
                    "column": None,
                })

        warnings.extend(report.warnings)

        return CompilationResult(
            success=report.is_valid,
            stage_reached="COMPLETED" if report.is_valid else "SEMANTIC_FAILED",
            query=clean_query,
            tokens=token_dicts,
            ast=ast_dict,
            ast_pretty=ast_pretty,
            semantic_report=report.to_dict(),
            errors=errors,
            warnings=warnings,
        )
