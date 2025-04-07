import os

RESERVED = {"end", "class", "flowchart", "graph", "click"}

def sanitize_node_id(task_id):
    return f"{task_id}_node" if task_id in RESERVED else task_id

def generate_mermaid_flowchart(task_ids):
    filtered_tasks = [task for task in task_ids if task.lower() not in ("start", "end")]
    if not filtered_tasks:
        return "[EMPTY TASK LIST]"

    mermaid_lines = ["flowchart TD"]
    mermaid_lines.append('    start["start"]')
    mermaid_lines.append(f'    start --> {sanitize_node_id(filtered_tasks[0])}["{filtered_tasks[0]}"]')

    for i in range(len(filtered_tasks) - 1):
        src = sanitize_node_id(filtered_tasks[i])
        tgt = sanitize_node_id(filtered_tasks[i + 1])
        mermaid_lines.append(f'    {src} --> {tgt}["{filtered_tasks[i + 1]}"]')

    mermaid_lines.append(f'    {sanitize_node_id(filtered_tasks[-1])} --> end_node["end"]')
    mermaid_lines.append('    end_node["end"]')
    return "\n".join(mermaid_lines)

def save_mermaid_chart_as_markdown(dag_file_path, dag_name, chart_str, output_dir="mermaid_charts"):
    os.makedirs(output_dir, exist_ok=True)
    file_name = os.path.splitext(os.path.basename(dag_file_path))[0]
    md_path = os.path.join(output_dir, f"{file_name}.md")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"### 📄 DAG File: `{dag_file_path}`\n")
        f.write(f"**DAG Name**: `{dag_name}`\n\n")
        f.write("```mermaid\n")
        f.write(chart_str)
        f.write("\n```\n")

    print(f"[SAVED] Mermaid chart saved to {md_path}")