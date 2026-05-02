from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="ipbd_kelompok3_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ipbd"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command="python /opt/airflow/src/extract/extract_from_csv.py",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command="python /opt/airflow/src/transform/clean_data.py",
    )

    load_staging = BashOperator(
        task_id="load_staging",
        bash_command="python /opt/airflow/src/load/load_to_staging.py",
    )

    load_warehouse = BashOperator(
        task_id="load_warehouse",
        bash_command="python /opt/airflow/src/load/load_to_warehouse.py",
    )

    extract >> transform >> load_staging >> load_warehouse