import os
from git import Repo

def clone_repo(repo_url, local_dir="cloned_repo"):
    if os.path.exists(local_dir):
        print(f"[INFO] Directory '{local_dir}' already exists. Skipping clone.")
    else:
        print(f"[INFO] Cloning repo from {repo_url} to {local_dir}...")
        Repo.clone_from(repo_url, local_dir)
        print("[INFO] Clone complete.")
    return local_dir

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