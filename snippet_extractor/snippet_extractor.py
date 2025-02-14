import ast
import pprint

class CodeDependencyAnalyzer(ast.NodeVisitor):
    def __init__(self, target_function, code):
        self.target_function = target_function
        self.code_lines = code.splitlines()  # Split code into lines
        self.dependencies = {
            'functions': set(),
            'methods': set(),
            'classes': set(),
            'variables': set(),
            'globals': set(),
            'imports': set(),
            'objects': set()  # Track object instantiations
        }
        self.dependency_lines = {
            'functions': [],
            'methods': [],
            'classes': [],
            'variables': [],
            'globals': [],
            'imports': [],
            'objects': []  # Track object instantiations
        }
        self.current_function = None
        self.target_function_lines = set()  # Track lines of the target function
        self.global_definitions = {}  # Track global variable definitions
        self.used_globals = set()  # Track global variables used in the target function
        self.global_objects = set()  # Track global objects (e.g., classes, functions)

    def visit_Import(self, node):
        # Track imported modules and their line numbers
        for alias in node.names:
            self.dependencies['imports'].add(alias.name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['imports'].append((alias.name, node.lineno, line))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Track imported entities from modules and their line numbers
        module = node.module
        for alias in node.names:
            full_name = f"{module}.{alias.name}"
            self.dependencies['imports'].add(full_name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['imports'].append((full_name, node.lineno, line))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Track functions and their line numbers
        if node.name == self.target_function:
            self.current_function = node.name
            # Record all lines of the target function
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            for line_no in range(start_line, end_line):
                self.target_function_lines.add(line_no)
            self.generic_visit(node)
            self.current_function = None
        else:
            # Track global function definitions
            self.global_objects.add(node.name)
            self.dependencies['functions'].add(node.name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['functions'].append((node.name, node.lineno, line))
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Track classes and their line numbers
        self.global_objects.add(node.name)
        self.dependencies['classes'].add(node.name)
        line = self.code_lines[node.lineno - 1]  # Get the line of code
        self.dependency_lines['classes'].append((node.name, node.lineno, line))
        self.generic_visit(node)

    def visit_Call(self, node):
        # Track function and method calls and their line numbers
        if isinstance(node.func, ast.Attribute):
            # Method call (e.g., obj.method())
            method_name = node.func.attr
            self.dependencies['methods'].add(method_name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['methods'].append((method_name, node.lineno, line))
        elif isinstance(node.func, ast.Name):
            # Function call (e.g., function())
            func_name = node.func.id
            if self.current_function == self.target_function:
                self.dependencies['functions'].add(func_name)
                line = self.code_lines[node.lineno - 1]  # Get the line of code
                self.dependency_lines['functions'].append((func_name, node.lineno, line))
        self.generic_visit(node)

    def visit_Name(self, node):
        # Track variable and global dependencies and their line numbers
        if isinstance(node.ctx, ast.Load):
            if self.current_function == self.target_function:
                # Track variables used in the target function
                self.dependencies['variables'].add(node.id)
                line = self.code_lines[node.lineno - 1]  # Get the line of code
                self.dependency_lines['variables'].append((node.id, node.lineno, line))
                # Track global variables used in the target function
                if node.id in self.global_definitions:
                    self.used_globals.add(node.id)
        self.generic_visit(node)

    def visit_Global(self, node):
        # Track global variables and their line numbers
        for name in node.names:
            self.dependencies['globals'].add(name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['globals'].append((name, node.lineno, line))
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Track variable assignments and their line numbers
        if self.current_function == self.target_function:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.dependencies['variables'].add(target.id)
                    line = self.code_lines[node.lineno - 1]  # Get the line of code
                    self.dependency_lines['variables'].append((target.id, node.lineno, line))
        elif isinstance(node.targets[0], ast.Name):
            # Track global variable definitions
            var_name = node.targets[0].id
            self.global_definitions[var_name] = node.lineno - 1  # Store the line number
        self.generic_visit(node)

    def visit_Expr(self, node):
        # Track object instantiations and their line numbers
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            # Object instantiation (e.g., obj = ClassName())
            class_name = node.value.func.id
            self.dependencies['objects'].add(class_name)
            line = self.code_lines[node.lineno - 1]  # Get the line of code
            self.dependency_lines['objects'].append((class_name, node.lineno, line))
        self.generic_visit(node)

    def analyze(self):
        tree = ast.parse("\n".join(self.code_lines))
        self.visit(tree)
        return self.dependencies, self.dependency_lines, self.target_function_lines, self.global_definitions, self.used_globals, self.global_objects


def extract_dependencies_with_code_lines(code, target_function):
    analyzer = CodeDependencyAnalyzer(target_function, code)
    dependencies, dependency_lines, target_function_lines, global_definitions, used_globals, global_objects = analyzer.analyze()
    return dependencies, dependency_lines, target_function_lines, global_definitions, used_globals, global_objects


class FunctionContextAnalyzer:
    def __init__(self, target_function=None, code=None):
        self.target_function = "__main__" if target_function is None else target_function
        self.code = """
            import sys
            if __name__ == "__main__":
                sys.exit(0)
                """ if code is None else code
        
        self.dependencies: dict
        self.dependency_lines: dict
        self.target_function_lines: set
        self.global_definitions: dict
        self.used_globals: set
        self.global_objects: set

    # Extract dependencies and their line numbers
    def analyze(self):
        self.dependencies, self.dependency_lines, self.target_function_lines, self.global_definitions, self.used_globals, self.global_objects = extract_dependencies_with_code_lines(self.code, self.target_function)

    # Print results
    def print_function_deps(self):
        print("Dependencies for function:", self.target_function)
        for category, items in self.dependencies.items():
            print(f"{category.capitalize()}:")
            for item in items:
                print(f"  - {item}")

        print("\nLines where dependencies occur:")
        for category, lines in self.dependency_lines.items():
            print(f"{category.capitalize()}:")
            for name, lineno, line in lines:
                print(f"  - {name} (Line {lineno}): {line}")

    def combine_and_sort_lines(self):
        # Combine all lines from all categories into a single list
        all_lines = []
        for category, lines in self.dependency_lines.items():
            all_lines.extend(lines)

        # Add lines of the target function
        for line_no in self.target_function_lines:
            line = self.code.splitlines()[line_no]
            all_lines.append(("target_function", line_no + 1, line))  # +1 to match line numbers

        # Add global definitions used in the target function
        for global_var in self.used_globals:
            if global_var in self.global_definitions:
                line_no = self.global_definitions[global_var]
                line = self.code.splitlines()[line_no]
                all_lines.append(("global_definition", line_no + 1, line))

        # Add global object definitions (e.g., classes, functions)
        for obj_name in self.global_objects:
            if obj_name in self.global_definitions:
                line_no = self.global_definitions[obj_name]
                line = self.code.splitlines()[line_no]
                all_lines.append(("global_object", line_no + 1, line))

        # Sort the lines by line number
        sorted_lines = sorted(all_lines, key=lambda x: x[1])  # Sort by line number (index 1)
        
        def dedup_lines(sorted_lines: list) -> list:
            seen_lines = set()
            unique_tuple_list = []
            for t in sorted_lines:
                if t[1] not in seen_lines:
                    unique_tuple_list.append(t)
                    seen_lines.add(t[1])
            return unique_tuple_list

        return dedup_lines(sorted_lines)
    
    def print_sorted_lines(self):
        csl = self.combine_and_sort_lines()
        pprint.pprint([ln[2] for ln in csl])

    def output_code_snippet(self):
        return "\n".join([t[2] for t in self.combine_and_sort_lines()])


def main(code=None):
    if code is None:
        code = """
import os
from math import sqrt

global_var = 10

x_ = 11

class ExampleClass:
    def method(self):
        print("Method called")

def helper_function():
    global global_var
    global_var += 6
    print("Helper function")

def example_function():
    global x_
    global global_var
    x = global_var
    
    x=5 * x_
    y = sqrt(x)
    helper_function()
    obj = ExampleClass()
    obj.method()
    """
    code2 = """
def example_function():
    
    y=x
    return y
    """
    fca = FunctionContextAnalyzer(code=code, target_function="example_function")
    fca.analyze()
    fca.print_function_deps() 
    fca.print_sorted_lines()
    print("# Final code snippet with dependencies, target function lines, and global definitions:")
    print(fca.output_code_snippet())

if __name__ == "__main__":
    # Inlined Python code as a string
    main()
