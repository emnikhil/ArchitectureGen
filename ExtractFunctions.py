import ast
import os
from collections import defaultdict

# ---- CONFIG ----
CLONED_REPO_PATH = "cloned_repo"
DAGS_FOLDER = os.path.join(CLONED_REPO_PATH, "dag_file")  # Adjust if needed


# ---- STEP 1: READ PYTHON FILES ----
def read_python_files(repo_dir):
    python_files = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        python_files.append((full_path, content))
                except Exception as e:
                    print(f"[ERROR] Reading {full_path}: {e}")
    return python_files


# ---- STEP 2: EXTRACT DAG TASKS ----
def extract_dags_and_tasks(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    dags = []
    tasks = []

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
                task_id = None
                callable_name = None
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


def process_all_dag_files():
    results = {}
    for root, _, files in os.walk(DAGS_FOLDER):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                dags, tasks = extract_dags_and_tasks(file_path)
                results[file_path] = {"dags": dags, "tasks": tasks}
    return results


# ---- STEP 3: INDEX AND RESOLVE FUNCTION DEFINITIONS ----
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


# ---- MAIN ----
if __name__ == "__main__":
    print("[INFO] Reading all Python files...")
    all_py_files = read_python_files(CLONED_REPO_PATH)

    print("[INFO] Indexing all DAG files...")
    all_dag_info = process_all_dag_files()

    print("[INFO] Indexing all function definitions...")
    func_index = index_all_functions(all_py_files)

    print("\n=========== DAG Task Function Mapping ===========\n")
    for path, info in all_dag_info.items():
        print(f"\n📄 DAG File: {path}")
        print("📌 DAGs:", info["dags"])
        resolved_tasks = resolve_task_functions(info["tasks"], func_index)

        for task_id, details in resolved_tasks.items():
            print(f"\n🔹 Task ID: {task_id}")
            print(f"    Function: {details['function_name']}")
            print(f"    File: {details['file']}")
            print(f"    Line: {details['lineno']}")
            print(f"    Logic:\n{details['source']}")
            print("-" * 60)
