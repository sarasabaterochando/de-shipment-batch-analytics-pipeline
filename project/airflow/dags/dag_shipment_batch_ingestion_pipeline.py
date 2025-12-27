from airflow import DAG
from pendulum import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import subprocess




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

    
    upload_to_gcs >> run_dataproc_job
