from airflow import DAG
from pendulum import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import subprocess
import os


DBT_PROJECT_DIR = os.environ["DBT_PROJECT_DIR"]
DBT_PROFILES_DIR = os.environ["DBT_PROFILES_DIR"]


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 12, 14),
    "depends_on_past": False,
    "retries": 1,
}



with DAG(
    dag_id="dag_docs",
    schedule="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:


    dbt_docs = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt docs generate --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_docs_serve = BashOperator(
        task_id='dbt_docs_serve',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt docs serve --port 8080 --profiles-dir {DBT_PROFILES_DIR} &',
    )

    dbt_docs >> dbt_docs_serve