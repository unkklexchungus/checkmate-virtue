#!/usr/bin/env python3
"""
Linting script to check for goto shadowing and other Playwright-related issues.
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple


class GotoShadowingChecker:
    """Check for goto shadowing in Python files."""
    
    def __init__(self):
        self.violations = []
    
    def check_file(self, file_path: Path) -> List[Tuple[int, int, str]]:
        """Check a single file for goto shadowing."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "goto":
                            violations.append((
                                node.lineno,
                                node.col_offset,
                                f"Variable 'goto' shadows Playwright page.goto method in {file_path}"
                            ))
                        elif isinstance(target, ast.Attribute):
                            if isinstance(target.value, ast.Name) and target.attr == "goto":
                                violations.append((
                                    node.lineno,
                                    node.col_offset,
                                    f"Assignment to page.goto shadows the method in {file_path}"
                                ))
                
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name) and node.target.id == "goto":
                        violations.append((
                            node.lineno,
                            node.col_offset,
                            f"Variable 'goto' shadows Playwright page.goto method in {file_path}"
                        ))
                
                elif isinstance(node, ast.For):
                    if isinstance(node.target, ast.Name) and node.target.id == "goto":
                        violations.append((
                            node.lineno,
                            node.col_offset,
                            f"Loop variable 'goto' shadows Playwright page.goto method in {file_path}"
                        ))
                
                elif isinstance(node, ast.With):
                    for item in node.items:
                        if isinstance(item.optional_vars, ast.Name) and item.optional_vars.id == "goto":
                            violations.append((
                                node.lineno,
                                node.col_offset,
                                f"With variable 'goto' shadows Playwright page.goto method in {file_path}"
                            ))
        
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
        
        return violations
    
    def check_directory(self, directory: Path) -> List[Tuple[int, int, str]]:
        """Check all Python files in a directory for goto shadowing."""
        all_violations = []
        
        for file_path in directory.rglob("*.py"):
            if file_path.name.startswith("__"):
                continue
            
            violations = self.check_file(file_path)
            all_violations.extend(violations)
        
        return all_violations


def main():
    """Main entry point."""
    print("=== Checking for Goto Shadowing Issues ===")
    
    checker = GotoShadowingChecker()
    
    # Check the qa directory
    qa_dir = Path(__file__).parent
    violations = checker.check_directory(qa_dir)
    
    if violations:
        print(f"❌ Found {len(violations)} goto shadowing violations:")
        for line, col, message in violations:
            print(f"  Line {line}, Column {col}: {message}")
        sys.exit(1)
    else:
        print("✅ No goto shadowing violations found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
