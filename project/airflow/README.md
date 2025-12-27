CREATE TABLE `agro-analytics-portfolio.batch_quality.fact_shipment_batch`
(
  shipment_batch_ID   STRING,
  package_class       STRING,
  total_weight_kg     FLOAT64,
  load_percentage_bp  INT64,
  package_count       INT64,
  routing_rules       STRING,
  destination_hubs    STRING
)
CLUSTER BY shipment_batch_ID, package_class;

CREATE TABLE IF NOT EXISTS `agro-analytics-portfolio.batch_quality.dim_shipment_batch`
(
  shipment_batch_ID   STRING,
  dispatch_date        TIMESTAMP,
  dispatch_time        STRING,
  completion_date      TIMESTAMP,
  completion_time      STRING,
  origin_facility_ID   STRING,
  shipment_category    STRING,
  handling_class       STRING,
  remarks              STRING,
  creation_data        TIMESTAMP
)
PARTITION BY DATE(creation_data);

para mi proyecto de data engineering quiero que me hagas un cuadro con el flujo completo. de un servidor local donde se almacenan archivos .ini SHIPMENT_BATCH con PACKAGE_TYPE blocks, he montado con Docker un orquetador de flujo Airflow 3.0. Con Airflow subo a un bucket de gcs los archivos ini raw, despues en airflow hay una tarea que ejecuta un job.sh que crea un cluster dataproc en google cloud que ejecuta el job que pasa los archivos del bucket a otro bucket en formato parquet, y de ese bucket en parquet los sube a bigquery. Al final del todo he creado un informe en power bi para la visualizacion de datos. Solo quiero que me crees una imagen gif con el flujo, que se muevan las flechas o lineas


## Google Cloud Resources

This project requires the following GCP resources:

- Google Cloud Project
- Cloud Storage Buckets:
  - Raw zone bucket
  - Curated (Parquet) zone bucket
- BigQuery Dataset
- Dataproc Cluster (ephemeral)
- Service Account with required permissions

All resource names are configured via environment variables.

añadir un .env.example
GCP_PROJECT=your-gcp-project-id
RAW_BUCKET=your-raw-bucket-name
PARQUET_BUCKET=your-parquet-bucket-name
BQ_DATASET=your_dataset
BQ_LOCATION=EU

# Ver todos los comandos disponibles
make help

# Generar terraform.tfvars desde airflow/config/config.env
make tfvars

cat terraform/terraform.tfvars

# Paso 2: Desplegar infraestructura (con confirmación)
make deploy

# Paso 3: Iniciar Airflow
make airflow-up

# Paso 4: Ver que todo funciona
make airflow-logs

# Cuando termines: Limpiar todo
make airflow-down
make destroy
make clean

# instalacion terraform en linux
# 1. Descargar e instalar Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update && sudo apt install terraform

# 2. Verificar instalación
terraform --version

```
Flujo completo:
config.env → Makefile (make tfvars) → terraform.tfvars → variables.tf → main.tf
   ↓              ↓                          ↓                ↓            ↓
 valores      genera tfvars            valores concretos   declaraciones  uso
Estructura recomendada:
terraform/
├── main.tf           # Recursos (lo que tienes)
├── variables.tf      # Declaraciones de variables (LO NECESITAS)
├── terraform.tfvars  # Valores (generado por Makefile)
└── outputs.tf        # (opcional pero recomendado)
```
Adding perms to the script dataproc
chmod +x airflow/scripts/deploy_dataproc_job.sh
