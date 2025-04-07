### 📄 DAG File: `cloned_repo/dag_file/crypto_dag.py`
**DAG Name**: `UnnamedDAG`

📌 **DAG Metadata:**
- DAG Name: `UnnamedDAG`
- Schedule: `@daily`
- Start Date: `2024-11-01`
- Owner: `data_engineer`
- Email: `alerts@example.com`

```mermaid
flowchart TD
    start["start"]
    start --> fetch_and_upload_data_gcs_task["fetch_and_upload_data_gcs_task"]
    fetch_and_upload_data_gcs_task --> load_data_bq_task["load_data_bq_task"]
    load_data_bq_task --> trigger_procedure_task["trigger_procedure_task"]
    trigger_procedure_task --> end_node["end"]
    end_node["end"]
```
