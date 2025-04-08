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