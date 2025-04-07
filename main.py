from clone_repo import clone_repo, read_python_files
from extract_dags import process_all_dag_files, index_all_functions, resolve_task_functions
from generate_chart import generate_mermaid_flowchart, save_mermaid_chart_as_markdown
import os

if __name__ == "__main__":
    REPO_URL = "https://github.com/emnikhil/Crypto-Data-Pipeline"
    CLONED_REPO_PATH = clone_repo(REPO_URL)
    DAGS_FOLDER = os.path.join(CLONED_REPO_PATH, "dag_file") #dags_folder_name

    print("[INFO] Reading all Python files...")
    all_py_files = read_python_files(CLONED_REPO_PATH)

    print("[INFO] Processing all DAG files...")
    all_dag_info = process_all_dag_files(DAGS_FOLDER)

    print("[INFO] Indexing all function definitions...")
    func_index = index_all_functions(all_py_files)

    print("\n=========== DAG Task Function Mapping ===========\n")
    for path, info in all_dag_info.items():
        print(f"\n📄 DAG File: {path}")
        print("📌 DAGs:", info["dags"])

        resolved_tasks = resolve_task_functions(info["tasks"], func_index)
        task_ids = list(resolved_tasks.keys())

        for task_id, details in resolved_tasks.items():
            print(f"\n🔹 Task ID: {task_id}")
            print(f"    Function: {details['function_name']}")
            print(f"    File: {details['file']}")
            print(f"    Line: {details['lineno']}")
            print(f"    Logic:\n{details['source']}")
            print("-" * 60)

        print("\n🧩 Mermaid Flowchart:")
        chart = generate_mermaid_flowchart(task_ids)
        print(chart)

        dag_name = info["dags"][0] if info["dags"] else "UnnamedDAG"
        save_mermaid_chart_as_markdown(path, dag_name, chart)

        print("=" * 80)