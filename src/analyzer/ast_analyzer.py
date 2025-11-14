"""
AST-based code analyzer to detect changes in Python code
"""
import ast
import os
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class CodeElement:
    """Represents a code element (function, class, etc.)"""
    name: str
    type: str  # 'function', 'class', 'method'
    line_start: int
    line_end: int
    complexity: int = 0


@dataclass
class FileAnalysis:
    """Analysis results for a file"""
    file_path: str
    functions: List[CodeElement]
    classes: List[CodeElement]
    imports: Set[str]
    total_lines: int
    complexity_score: int


class ASTAnalyzer:
    """Analyzes Python code using AST"""

    def analyze_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze a Python file and extract code elements"""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code, filename=file_path)

            functions = []
            classes = []
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = CodeElement(
                        name=node.name,
                        type='function',
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        complexity=self._calculate_complexity(node)
                    )
                    functions.append(element)

                elif isinstance(node, ast.ClassDef):
                    element = CodeElement(
                        name=node.name,
                        type='class',
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        complexity=self._calculate_complexity(node)
                    )
                    classes.append(element)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.update(self._extract_imports(node))

            total_lines = len(source_code.split('\n'))
            complexity_score = sum(f.complexity for f in functions) + sum(c.complexity for c in classes)

            return FileAnalysis(
                file_path=file_path,
                functions=functions,
                classes=classes,
                imports=imports,
                total_lines=total_lines,
                complexity_score=complexity_score
            )

        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def compare_files(self, old_analysis: FileAnalysis, new_analysis: FileAnalysis) -> Dict:
        """Compare two file analyses to detect changes"""
        changes = {
            'file_path': new_analysis.file_path,
            'functions_added': [],
            'functions_removed': [],
            'functions_modified': [],
            'classes_added': [],
            'classes_removed': [],
            'classes_modified': [],
            'imports_added': [],
            'imports_removed': [],
            'lines_changed': abs(new_analysis.total_lines - old_analysis.total_lines),
            'complexity_delta': new_analysis.complexity_score - old_analysis.complexity_score
        }

        # Compare functions
        old_funcs = {f.name: f for f in old_analysis.functions}
        new_funcs = {f.name: f for f in new_analysis.functions}

        changes['functions_added'] = [f for f in new_funcs.keys() if f not in old_funcs]
        changes['functions_removed'] = [f for f in old_funcs.keys() if f not in new_funcs]

        for func_name in set(old_funcs.keys()) & set(new_funcs.keys()):
            if (old_funcs[func_name].line_end - old_funcs[func_name].line_start !=
                new_funcs[func_name].line_end - new_funcs[func_name].line_start):
                changes['functions_modified'].append(func_name)

        # Compare classes
        old_classes = {c.name: c for c in old_analysis.classes}
        new_classes = {c.name: c for c in new_analysis.classes}

        changes['classes_added'] = [c for c in new_classes.keys() if c not in old_classes]
        changes['classes_removed'] = [c for c in old_classes.keys() if c not in new_classes]

        for class_name in set(old_classes.keys()) & set(new_classes.keys()):
            if (old_classes[class_name].line_end - old_classes[class_name].line_start !=
                new_classes[class_name].line_end - new_classes[class_name].line_start):
                changes['classes_modified'].append(class_name)

        # Compare imports
        changes['imports_added'] = list(new_analysis.imports - old_analysis.imports)
        changes['imports_removed'] = list(old_analysis.imports - new_analysis.imports)

        return changes

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a node"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Add complexity for control flow statements
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1

        return complexity

    def _extract_imports(self, node: ast.AST) -> Set[str]:
        """Extract import names from import nodes"""
        imports = set()

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.add(f"{module}.{alias.name}" if module else alias.name)

        return imports

    def get_changed_elements(self, changes: Dict) -> Set[str]:
        """Get set of all changed element names"""
        changed = set()
        changed.update(changes.get('functions_added', []))
        changed.update(changes.get('functions_removed', []))
        changed.update(changes.get('functions_modified', []))
        changed.update(changes.get('classes_added', []))
        changed.update(changes.get('classes_removed', []))
        changed.update(changes.get('classes_modified', []))
        return changed
