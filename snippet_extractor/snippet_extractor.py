import ast
import os

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, target_func, code):
        self.target_func = target_func
        self.code_lines = code.splitlines()
        self.deps = {category: set() for category in [
            'functions', 'methods', 'classes', 'variables', 'globals', 'imports', 'objects'
        ]}
        self.dep_lines = {category: [] for category in self.deps}
        self.current_func = None
        self.target_func_lines = set()
        self.global_vars = {}
        self.used_globals = set()
        self.global_objs = set()

    def visit_Import(self, node):
        for alias in node.names:
            self._add_dep('imports', alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            full_name = f"{module}.{alias.name}"
            self._add_dep('imports', full_name, node.lineno)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name == self.target_func:
            self.current_func = node.name
            self._record_func_lines(node)
            self.generic_visit(node)
            self.current_func = None
        else:
            self.global_objs.add(node.name)
            self._add_dep('functions', node.name, node.lineno)
            self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.global_objs.add(node.name)
        self._add_dep('classes', node.name, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            self._add_dep('methods', node.func.attr, node.lineno)
        elif isinstance(node.func, ast.Name) and self.current_func == self.target_func:
            self._add_dep('functions', node.func.id, node.lineno)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and self.current_func == self.target_func:
            self._add_dep('variables', node.id, node.lineno)
            if node.id in self.global_vars:
                self.used_globals.add(node.id)
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self._add_dep('globals', name, node.lineno)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if self.current_func == self.target_func:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._add_dep('variables', target.id, node.lineno)
        elif isinstance(node.targets[0], ast.Name):
            self.global_vars[node.targets[0].id] = node.lineno - 1
        self.generic_visit(node)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            self._add_dep('objects', node.value.func.id, node.lineno)
        self.generic_visit(node)

    def _add_dep(self, category, name, lineno):
        self.deps[category].add(name)
        self.dep_lines[category].append((name, lineno, self.code_lines[lineno - 1]))

    def _record_func_lines(self, node):
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
        self.target_func_lines.update(range(start_line, end_line))

    def analyze(self):
        tree = ast.parse("\n".join(self.code_lines))
        self.visit(tree)
        return self.deps, self.dep_lines, self.target_func_lines, self.global_vars, self.used_globals, self.global_objs


def extract_deps(code, target_func):
    analyzer = CodeAnalyzer(target_func, code)
    return analyzer.analyze()


class FunctionAnalyzer:
    def __init__(self, target_func=None, code=None):
        self.target_func = "__main__" if target_func is None else target_func
        self.code = """
            import sys
            if __name__ == "__main__":
                sys.exit(0)
                """ if code is None else code
        self.deps = {}
        self.dep_lines = {}
        self.target_func_lines = set()
        self.global_vars = {}
        self.used_globals = set()
        self.global_objs = set()

    def analyze(self):
        self.deps, self.dep_lines, self.target_func_lines, self.global_vars, self.used_globals, self.global_objs = extract_deps(self.code, self.target_func)

    def print_deps(self):
        print("Dependencies for function:", self.target_func)
        for category, items in self.deps.items():
            print(f"{category.capitalize()}:")
            for item in items:
                print(f"  - {item}")

        for category, lines in self.dep_lines.items():
            print(f"{category.capitalize()}:")
            for name, lineno, line in lines:
                print(f"  - {name} (Line {lineno}): {line}")

    def combine_and_sort_lines(self):
        all_lines = []
        for category, lines in self.dep_lines.items():
            all_lines.extend(lines)

        for line_no in self.target_func_lines:
            all_lines.append(("target_function", line_no + 1, self.code.splitlines()[line_no]))

        for global_var in self.used_globals:
            if global_var in self.global_vars:
                line_no = self.global_vars[global_var]
                all_lines.append(("global_definition", line_no + 1, self.code.splitlines()[line_no]))

        for obj_name in self.global_objs:
            if obj_name in self.global_vars:
                line_no = self.global_vars[obj_name]
                all_lines.append(("global_object", line_no + 1, self.code.splitlines()[line_no]))

        sorted_lines = sorted(all_lines, key=lambda x: x[1])
        return self._dedup_lines(sorted_lines)

    def _dedup_lines(self, sorted_lines):
        seen = set()
        return [t for t in sorted_lines if t[1] not in seen and not seen.add(t[1])]

    def print_sorted_lines(self):
        for line in self.combine_and_sort_lines():
            print(line[2])

    def output_code_snippet(self):
        return "\n".join([t[2] for t in self.combine_and_sort_lines()])


def parse_files(file_paths):
    parsed = {}
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            parsed[file_path] = file.read()
    return parsed


def find_target_file(parsed_files, target_func):
    for file_path, code in parsed_files.items():
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == target_func:
                return file_path, code
    return None, None


def process_deps(parsed_files, target_func, processed=None):
    if processed is None:
        processed = set()
    
    if target_func in processed:
        return ""
    
    processed.add(target_func)
    
    target_file, target_code = find_target_file(parsed_files, target_func)
    if not target_file:
        return ""
    
    analyzer = FunctionAnalyzer(target_func=target_func, code=target_code)
    analyzer.analyze()
    code_snippet = analyzer.output_code_snippet()
    
    for dep in analyzer.deps['imports']:
        prefix = f"\n\n# Dependencies from {dep}:\n"
        if '.' in dep:
            _, func = dep.split('.')
            code_snippet += prefix + process_deps(parsed_files, func, processed)
        else:
            code_snippet += prefix + process_deps(parsed_files, dep, processed)
    
    return code_snippet


def main(file_paths, target_func):
    parsed_files = parse_files(file_paths)
    code_snippet = process_deps(parsed_files, target_func)
    print("# Final code snippet with dependencies:")
    print(code_snippet)


if __name__ == "__main__":
    file_paths = ['tests' + os.sep + 'file1.py', 'tests' + os.sep + 'file2.py']
    target_function = "main_function"
    main(file_paths, target_function)
