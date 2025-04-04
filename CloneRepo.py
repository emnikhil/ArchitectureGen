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
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    python_files.append((full_path, content))
    return python_files

if __name__ == "__main__":
    repo_url = "https://github.com/emnikhil/Crypto-Data-Pipeline"
    local_repo = clone_repo(repo_url)
    all_py_files = read_python_files(local_repo)

    print(f"\n[INFO] Total Python files found: {len(all_py_files)}\n")
    for path, content in all_py_files[:3]:
        print(f"File: {path}\n{'-'*40}\n{content[:300]}...\n{'='*60}\n")