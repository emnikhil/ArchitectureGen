from clone_repo import clone_repo, read_python_files
from extract_dags import process_all_dag_files, index_all_functions, resolve_task_functions
from generate_chart import generate_mermaid_flowchart
import os
import shutil

def process_repo(REPO_URL):
    CLONED_REPO_PATH = clone_repo(REPO_URL)
    DAGS_FOLDER = os.path.join(CLONED_REPO_PATH, "dag_file")

    all_py_files = read_python_files(CLONED_REPO_PATH)
    all_dag_info = process_all_dag_files(DAGS_FOLDER)
    func_index = index_all_functions(all_py_files)//

    results = []

    for path, info in all_dag_info.items():
        try:
            resolved_tasks = resolve_task_functions(info["tasks"], func_index)
            task_ids = list(resolved_tasks.keys())
            chart = generate_mermaid_flowchart(task_ids)

            dag_name = info["dags"][0] if info["dags"] else "UnnamedDAG"
            results.append((dag_name, chart))
        except Exception as e:
            all_successful = False
            print(f"[ERROR] Failed to process DAG file {path}: {e}")

    return results