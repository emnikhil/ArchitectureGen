import ast
import os
from collections import defaultdict

RESERVED = {"end", "class", "flowchart", "graph", "click"}

def sanitize_node_id(task_id):
    return f"{task_id}_node" if task_id in RESERVED else task_id

def extract_dags_and_tasks(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    dags, tasks = [], []

    class DAGVisitor(ast.NodeVisitor):
        def visit_With(self, node):
            for item in node.items:
                context_expr = item.context_expr
                if isinstance(context_expr, ast.Call):
                    if isinstance(context_expr.func, ast.Name) and context_expr.func.id == "DAG":
                        dag_id = None
                        for kw in context_expr.keywords:
                            if kw.arg == "dag_id" and isinstance(kw.value, ast.Str):
                                dag_id = kw.value.s
                        if dag_id:
                            dags.append(dag_id)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) or isinstance(node.func, ast.Attribute):
                task_id, callable_name = None, None
                for kw in node.keywords:
                    if kw.arg == "task_id" and isinstance(kw.value, ast.Str):
                        task_id = kw.value.s
                    if kw.arg == "python_callable" and isinstance(kw.value, ast.Name):
                        callable_name = kw.value.id
                if task_id:
                    tasks.append((task_id, callable_name))
            self.generic_visit(node)

    DAGVisitor().visit(tree)
    return dags, tasks

def process_all_dag_files(dag_folder):
    results = {}
    for root, _, files in os.walk(dag_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                dags, tasks = extract_dags_and_tasks(file_path)
                results[file_path] = {"dags": dags, "tasks": tasks}
    return results

def index_all_functions(py_files):
    func_index = defaultdict(list)
    for file_path, content in py_files:
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            continue

        class FunctionCollector(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                try:
                    func_source = ast.unparse(node)
                except Exception:
                    func_source = f"[source unavailable - Python <3.9] {node.name}"

                func_index[node.name].append({
                    "file": file_path,
                    "lineno": node.lineno,
                    "source": func_source
                })
                self.generic_visit(node)

        FunctionCollector().visit(tree)
    return func_index

def resolve_task_functions(tasks, func_index):
    resolved = {}
    for task_id, callable_name in tasks:
        if not callable_name:
            continue
        candidates = func_index.get(callable_name)
        if candidates:
            func_info = candidates[0]
            resolved[task_id] = {
                "function_name": callable_name,
                "file": func_info["file"],
                "lineno": func_info["lineno"],
                "source": func_info["source"]
            }
        else:
            resolved[task_id] = {
                "function_name": callable_name,
                "file": None,
                "lineno": None,
                "source": "[UNRESOLVED]"
            }
    return resolved