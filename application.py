import streamlit as st
import streamlit.components.v1 as components
import os
import shutil
import time
from urllib.parse import urlparse

from clone_repo import clone_repo, read_python_files
from extract_dags import process_all_dag_files, index_all_functions, resolve_task_functions
from generate_chart import generate_mermaid_flowchart

def get_repo_name(repo_url):
    return urlparse(repo_url).path.rstrip("/").split("/")[-1]

def render_mermaid(mermaid_code: str):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <div class="mermaid">
        {mermaid_code}
        </div>
        <script>
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=500,
        scrolling=True,
    )

st.title("📊 ArchitectureGen")

repo_url = st.text_input("🔗 Enter GitHub Repo URL", placeholder="https://github.com/repo")
start = st.button("🚀 Start Process")

if start:
    if not repo_url:
        st.warning("⚠️ Please enter a valid GitHub repo URL.")
    else:
        status = st.empty()
        chart_outputs = []

        try:
            repo_name = get_repo_name(repo_url)

            status.info("📦 Cloning Repository...")
            CLONED_REPO_PATH = clone_repo(repo_url)
            time.sleep(1)

            status.info("📄 Reading Python files...")
            all_py_files = read_python_files(CLONED_REPO_PATH)
            time.sleep(1)

            status.info("🔍 Extracting DAG info...")
            dags_folder = os.path.join(CLONED_REPO_PATH, "dag_file")
            all_dag_info = process_all_dag_files(dags_folder)
            time.sleep(1)

            status.info("🧠 Indexing Functions...")
            func_index = index_all_functions(all_py_files)
            time.sleep(1)

            status.info("🧩 Generating Mermaid charts...")
            for path, info in all_dag_info.items():
                try:
                    resolved_tasks = resolve_task_functions(info["tasks"], func_index)
                    task_ids = list(resolved_tasks.keys())
                    chart = generate_mermaid_flowchart(task_ids)

                    dag_name = info["dags"][0] if info["dags"] else repo_name
                    chart_outputs.append((dag_name, chart))
                except Exception as e:
                    st.error(f"❌ Failed to process DAG file {path}: {e}")

            status.success("✅ Process Complete! Charts ready below.")

            if chart_outputs:
                if len(chart_outputs) == 1:
                    dag_name, chart = chart_outputs[0]
                    st.markdown(f"#### 📁 {dag_name}")
                    render_mermaid(chart)
                else:
                    dag_names = [name for name, _ in chart_outputs]
                    selected_dag = st.selectbox("📂 Select a DAG to view", dag_names)
                    selected_chart = next(item for item in chart_outputs if item[0] == selected_dag)
                    st.markdown(f"#### 📁 {selected_dag}")
                    render_mermaid(selected_chart[1])
            else:
                st.info("ℹ️ No charts available. No valid DAGs found.")
        except Exception as e:
            status.error(f"❌ Failed to process repository: {e}")
        finally:
            if 'CLONED_REPO_PATH' in locals() and os.path.exists(CLONED_REPO_PATH):
                try:
                    shutil.rmtree(CLONED_REPO_PATH)
                    status.info("🧹 Cloned repository cleaned up from disk.")
                except Exception as e:
                    status.warning(f"⚠️ Could not delete cloned repository: {e}")