from airflow import DAG
from pendulum import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import subprocess
import os


DBT_PROJECT_DIR = os.environ["DBT_PROJECT_DIR"]
DBT_PROFILES_DIR = os.environ["DBT_PROFILES_DIR"]

def run_python_gcs_storage():
    subprocess.run(["python3", "/opt/airflow/scripts/local_to_gcs_batch_file_ingestion.py"], check=True)

def run_dataproc_bash():
    subprocess.run(['/opt/airflow/scripts/deploy_dataproc_job.sh'], check=True)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 12, 14),
    "depends_on_past": False,
    "retries": 1,
}




with DAG(
    dag_id="dag_shipment_batch_ingestion_pipeline",
    schedule="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:




    upload_to_gcs = PythonOperator(
        task_id="upload_batches_to_gcs",
        python_callable=run_python_gcs_storage,
    )


    run_dataproc_job = PythonOperator(
         task_id="run_dataproc_processing_job",
         python_callable=run_dataproc_bash,
    )

    # dbt staging
    dbt_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select staging --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select staging --profiles-dir {DBT_PROFILES_DIR}',
    )

    # dbt intermediate
    dbt_intermediate = BashOperator(
        task_id='dbt_run_intermediate',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select intermediate --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_test_intermediate = BashOperator(
        task_id='dbt_test_intermediate',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select intermediate --profiles-dir {DBT_PROFILES_DIR}',
    )

    # dbt dimensions
    dbt_dimensions = BashOperator(
        task_id='dbt_run_dimensions',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select marts.dimensions --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_test_dimensions = BashOperator(
        task_id='dbt_test_dimensions',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select marts.dimensions --profiles-dir {DBT_PROFILES_DIR}',
    )

    # dbt facts
    dbt_facts = BashOperator(
        task_id='dbt_run_facts',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --select marts.facts --profiles-dir {DBT_PROFILES_DIR}',
    )

    dbt_test_facts = BashOperator(
        task_id='dbt_test_facts',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --select marts.facts --profiles-dir {DBT_PROFILES_DIR}',
    )

   
    upload_to_gcs >> run_dataproc_job \
    >> dbt_staging >> dbt_test_staging \
    >> dbt_intermediate >> dbt_test_intermediate \
    >> dbt_dimensions >> dbt_test_dimensions \
    >> dbt_facts >> dbt_test_facts 