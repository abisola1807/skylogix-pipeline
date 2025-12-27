from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/home/abisola_1807/skylogix-pipeline"
PIPELINE_PY = f"{PROJECT_DIR}/venv/bin/python"  # your pipeline venv python

default_args = {
    "owner": "skylogix",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_pipeline",
    default_args=default_args,
    description="SkyLogix Weather Data Pipeline (MongoDB -> PostgreSQL)",
    start_date=datetime(2025, 12, 26),
    schedule="*/15 * * * *",   # every 15 minutes
    catchup=False,
    tags=["skylogix", "weather"],
) as dag:

    fetch_upsert = BashOperator(
        task_id="fetch_and_upsert_raw",
        bash_command=f"cd {PROJECT_DIR} && {PIPELINE_PY} scripts/ingest_weather.py",
    )

    transform_load = BashOperator(
        task_id="transform_and_load_postgres",
        bash_command=f"cd {PROJECT_DIR} && {PIPELINE_PY} scripts/transform_load.py",
    )

    fetch_upsert >> transform_load
