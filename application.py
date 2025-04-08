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

def render_mermaid(mermaid_code: str, dag_name: str = "mermaid_chart"):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />

        <style>
            .download-icon {{
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                padding: 8px;
                cursor: pointer;
                display: none;
                z-index: 10;
            }}
            .mermaid-container:hover .download-icon {{
                display: block;
            }}
        </style>

        <div class="mermaid-container" id="capture">
            <div class="download-icon" onclick="downloadImage()" title="Download">
                <i class="fa-solid fa-download"></i>
            </div>
            <div class="mermaid">
                {mermaid_code}
            </div>
        </div>

        <script>
            mermaid.initialize({{ startOnLoad: true }});

            function downloadImage() {{
                var element = document.getElementById("capture");
                html2canvas(element).then(function(canvas) {{
                    var link = document.createElement("a");
                    link.download = "{dag_name}.png";
                    link.href = canvas.toDataURL("image/png");
                    link.click();
                }});
            }}
        </script>
        """,
        height=600,
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
            print(f"[LOG] Cloning repo: {repo_url}")
            CLONED_REPO_PATH = clone_repo(repo_url)
            time.sleep(1)

            status.info("📄 Reading Python files...")
            print("[LOG] Reading all .py files in repo")
            all_py_files = read_python_files(CLONED_REPO_PATH)
            time.sleep(1)

            status.info("🔍 Extracting DAG info...")
            dags_folder = os.path.join(CLONED_REPO_PATH, "dag_file")
            print(f"[LOG] Processing folder for DAGs: {dags_folder}")
            all_dag_info = process_all_dag_files(dags_folder)
            time.sleep(1)

            status.info("🧠 Indexing Functions...")
            print("[LOG] Indexing all Python functions")
            func_index = index_all_functions(all_py_files)
            time.sleep(1)

            status.info("🧩 Generating Mermaid charts...")
            print("[LOG] Creating charts from DAGs")
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
                    render_mermaid(chart, dag_name)
                else:
                    dag_names = [name for name, _ in chart_outputs]
                    selected_dag = st.selectbox("📂 Select a DAG to view", dag_names)
                    selected_chart = next(item for item in chart_outputs if item[0] == selected_dag)
                    st.markdown(f"#### 📁 {selected_dag}")
                    render_mermaid(selected_chart[1], selected_dag)
            else:
                st.info("ℹ️ No charts available. No valid DAGs found.")
        except Exception as e:
            status.error(f"❌ Failed to process repository: {e}")
            print(f"[ERROR] {e}")
        finally:
            if 'CLONED_REPO_PATH' in locals() and os.path.exists(CLONED_REPO_PATH):
                try:
                    shutil.rmtree(CLONED_REPO_PATH)
                    print("[LOG] Deleted cloned repo from disk.")
                    status.info("🧹 Cloned repository cleaned up from disk.")
                except Exception as e:
                    print(f"[WARNING] Failed to delete repo: {e}")
                    status.warning(f"⚠️ Could not delete cloned repository: {e}")