from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="ipbd_kelompok3_pipeline",
    description="ETL pipeline harga pangan kelompok 3",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ipbd", "etl", "kelompok3"],
) as dag:

    extract_2024 = BashOperator(
        task_id="extract_data_2024",
        bash_command="python /opt/airflow/src/extract/scrape_pihps_2024.py",
    )

    extract_2025 = BashOperator(
        task_id="extract_data_2025",
        bash_command="python /opt/airflow/src/extract/scrape_pihps_2025.py",
    )

    transform = BashOperator(
        task_id="transform_clean_data",
        bash_command="python /opt/airflow/src/transform/clean_data.py",
    )

    load = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/airflow/src/load/load_to_db.py",
    )

    [extract_2024, extract_2025] >> transform >> load