#!/usr/bin/env python3
"""
Custom ruff rules to prevent Playwright goto method shadowing.
This file contains rules that detect potential shadowing of page.goto.
"""

import ast
from typing import Iterator, Tuple

import ruff


class GotoShadowingVisitor(ast.NodeVisitor):
    """AST visitor to detect goto shadowing."""
    
    def __init__(self):
        self.goto_assignments = []
        self.page_objects = set()
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment nodes to detect goto assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "goto":
                self.goto_assignments.append((node.lineno, node.col_offset))
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name) and target.attr == "goto":
                    # This is page.goto = something, which shadows the method
                    self.goto_assignments.append((node.lineno, node.col_offset))
        
        self.generic_visit(node)
    
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignment nodes."""
        if isinstance(node.target, ast.Name) and node.target.id == "goto":
            self.goto_assignments.append((node.lineno, node.col_offset))
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        """Visit for loop nodes to detect goto in loop variables."""
        if isinstance(node.target, ast.Name) and node.target.id == "goto":
            self.goto_assignments.append((node.lineno, node.col_offset))
        
        self.generic_visit(node)
    
    def visit_With(self, node: ast.With) -> None:
        """Visit with statement nodes."""
        for item in node.items:
            if isinstance(item.optional_vars, ast.Name) and item.optional_vars.id == "goto":
                self.goto_assignments.append((node.lineno, node.col_offset))
        
        self.generic_visit(node)


def check_goto_shadowing(tree: ast.AST) -> Iterator[Tuple[int, int, str]]:
    """
    Check for goto shadowing in the AST.
    
    Args:
        tree: The AST to check
        
    Yields:
        Tuple of (line, column, message) for each violation
    """
    visitor = GotoShadowingVisitor()
    visitor.visit(tree)
    
    for line, col in visitor.goto_assignments:
        yield (
            line,
            col,
            "GOTO001: Variable 'goto' shadows Playwright page.goto method. Use a different variable name."
        )


# Register the rule with ruff
ruff.register_rule("GOTO001", check_goto_shadowing)
