# Shipment Batch Analytics Pipeline

A data engineering project that processes shipment batch files using Google Cloud Platform services. The pipeline reads .ini files, processes them with PySpark on Dataproc, stores the data in BigQuery, and creates reports with Power BI.

## Project Overview

This pipeline handles shipment batch data through these stages:
1. Upload .ini files to Google Cloud Storage (raw bucket)
2. Process files with PySpark on Dataproc cluster
3. Convert data to Parquet format and store in GCS
4. Load processed data into BigQuery tables
5. Connect Power BI to BigQuery for data cleaning and analysis

The infrastructure is managed with Terraform and the workflow is orchestrated with Apache Airflow.

## Architecture
![Architecture-diagram](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/images/Diagrama.jpg)  
```
.ini files → GCS (raw) → Dataproc (PySpark) → GCS (parquet) → BigQuery → Power BI
```

## Technologies Used

- **Google Cloud Platform**: Cloud infrastructure
- **Terraform**: Infrastructure as code
- **Apache Airflow**: Workflow orchestration
- **Dataproc**: Managed Spark clusters
- **PySpark**: Data processing
- **BigQuery**: Data warehouse
- **Power BI**: Data visualization and analysis
- **Docker**: Containerization for Airflow

## Project Structure
```
project/
├── airflow/
│   ├── config/
│   │   └── config.env
│   ├── dags/
│   │   └── dag_shipment_batch_ingestion_pipeline.py
│   ├── scripts/
│   │   ├── deploy_dataproc_job.sh
│   │   └── local_to_gcs_batch_file_ingestion.py
│   ├── .google/credentials/
│   │   └── google_credentials.json
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
│   ├── spark/
│   │   └── gcs_to_bigquery_upload.py
│   └── create_bq_tables.py
├── sql/
│   ├── dim_batch_shipment.sql
│   └── fact_batch_shipment.sql
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── Makefile
```

## Prerequisites

Before starting, you need:

1. A Google Cloud Platform project created
2. Terraform installed (version >= 1.5.0)
3. Docker and Docker Compose installed
4. Python 3.x installed
5. GCP service account with necessary permissions:
   - Storage Admin
   - BigQuery Admin
   - Dataproc Admin

## Setup Instructions

### 1. Configure Environment Variables

Edit the `airflow/config/config.env` file with your GCP project details:
```bash
# Google Cloud configuration
PROJECT_ID=your-project-id
REGION=your-region

# Dataproc cluster configuration
CLUSTER_NAME=your-cluster-name
IMAGE_VERSION=2.1-debian11
MACHINE_TYPE=e2-standard-2
BOOT_DISK_SIZE=100
REGION_CLUSTER=us-central1

# Google Cloud Storage buckets
RAW_BUCKET=your-raw-bucket-name
PARQUET_BUCKET=your-parquet-bucket-name
CODE_BUCKET=your-code-bucket-name
PROCESSED_PREFIX=processed/
RAW_PREFIX=archivos_raw/
GCS_LOCATION=us-central1
GCS_STORAGE_CLASS=STANDARD

# Spark job
SPARK_JOB=gs://your-code-bucket/scripts/spark/gcs_to_bigquery_upload.py

# Service Account
SERVICE_ACCOUNT=your-service-account@your-project.iam.gserviceaccount.com
USER_EMAIL=your-email@gmail.com

# BigQuery
BQ_DATASET=your-dataset-name
BQ_TABLE_FACT=fact_table_name
BQ_TABLE_DIM=dim_table_name
BQ_LOCATION=US
```

### 2. Add Service Account Credentials

Place your GCP service account JSON key file in:
```
airflow/.google/credentials/google_credentials.json
```

### 3. Configure .ini Files Path

In the `airflow/docker-compose.yml` file, update the volume path for your .ini files:
```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
  - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
  - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
  - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
  - ${AIRFLOW_PROJ_DIR:-.}/.google/credentials:/opt/airflow/.google/credentials
  - ${AIRFLOW_PROJ_DIR:-.}/scripts:/opt/airflow/scripts
  - your_path/ini_files:/opt/airflow/ini_files  # Replace 'your_path' with your actual path
```

Replace `your_path/ini_files` with the full path to your local folder containing the .ini files.

Example:
```yaml
- /home/user/data/ini_files:/opt/airflow/ini_files
```

### 4. Deploy Infrastructure with Terraform
```bash
# Initialize Terraform
make init

# Review the plan
make plan

# Apply infrastructure
make apply
```

This will create:
- Three GCS buckets (raw data, parquet data, processing code)
- BigQuery dataset
- Upload the PySpark script to the code bucket

### 5. Create BigQuery Tables
```bash
make create-bq-tables
```

### 6. Start Airflow
```bash
make airflow-up
```

Access Airflow UI at `http://localhost:8080`

Default credentials:
- Username: `airflow`
- Password: `airflow`

## How It Works

### Daily Pipeline (Airflow DAG)

The pipeline runs daily and consists of two main tasks:

1. **upload_batches_to_gcs**: Uploads new .ini files from local directory to GCS raw bucket
   - Checks which files were already processed
   - Only uploads new files
   - Updates processing state in GCS

2. **run_dataproc_processing_job**: Processes the files with PySpark
   - Creates a Dataproc cluster
   - Runs the PySpark job to parse .ini files
   - Converts data to Parquet format
   - Loads data into BigQuery
   - Deletes the cluster after completion

![Airflow-dags](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/images/airflow-image.jpg)

### Data Model

The pipeline creates two tables in BigQuery:

**Dimension Table (dim_batch_shipment)**:
- shipment_batch_ID
- dispatch_date
- dispatch_time
- completion_date
- completion_time
- origin_facility_ID
- shipment_category
- handling_class
- remarks
- creation_data

**Fact Table (fact_batch_shipment)**:
- shipment_batch_ID
- package_class
- total_weight_kg
- load_percentage_bp
- package_count
- routing_rules
- destination_hubs

## Available Make Commands
```bash
make help              # Show all available commands
make init             # Initialize Terraform
make plan             # View infrastructure changes
make apply            # Deploy infrastructure
make destroy          # Destroy infrastructure
make create-bq-tables # Create BigQuery tables
make airflow-up       # Start Airflow
make airflow-down     # Stop Airflow
make airflow-logs     # Show Airflow logs
make clean            # Clean generated files
```

## Power BI Integration

[PowerBI Demonstration](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/PowerBI/powerBI.gif)  
After the data is loaded into BigQuery:

1. Connect Power BI to your BigQuery project
2. Import the two tables: `dim_batch_shipment` and `fact_batch_shipment`
3. Perform data cleaning and transformations in Power BI
4. Create your analysis and visualizations

### Using the Power BI Template

A ready-to-use Power BI template is included in the `powerbi/` folder:
```
powerbi/
└── shipment_project.pbit
```

To use it:

1. Open `shipment_project.pbit` in Power BI Desktop
2. When prompted, enter your BigQuery connection details:
   - Project ID
   - Dataset name
3. The template will automatically connect to your tables and load all the analysis

The template includes:
- Pre-configured data model with relationships
- Data cleaning transformations
- Dashboard visualizations
- Custom measures and calculations

## Cleaning Up

To destroy all infrastructure:
```bash
make destroy
```

To stop Airflow:
```bash
make airflow-down
```

## Notes

- The Dataproc cluster is created and deleted automatically for each run to save costs
- The pipeline uses a state file in GCS to track processed files
- BigQuery must be in the same Region than PowerBI.
