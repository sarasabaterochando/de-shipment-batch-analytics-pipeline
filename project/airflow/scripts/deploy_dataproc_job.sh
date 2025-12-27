#!/bin/bash
set -euo pipefail

# Load environment variables
set -o allexport
source ./config/config.env
set +o allexport


REQUIRED_VARS=(
    PROJECT_ID
    REGION
    CLUSTER_NAME
    IMAGE_VERSION
    MACHINE_TYPE
    BOOT_DISK_SIZE
    RAW_BUCKET
    PARQUET_BUCKET
    CODE_BUCKET
    SPARK_JOB
    SERVICE_ACCOUNT
    USER_EMAIL
    BQ_DATASET
    BQ_TABLE_FACT
    BQ_TABLE_DIM
    REGION_CLUSTER
)

for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "Error: Required environment variable '$var' is not set."
        exit 1
    fi
done

# Set project for gcloud
export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"
export GOOGLE_APPLICATION_CREDENTIALS="/opt/airflow/.google/credentials/google_credentials.json"

# Authenticate with service account
echo "Activating service account..."
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

# Authenticate with GCP (ADC)
if [[ -z "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
    echo "Error: GOOGLE_APPLICATION_CREDENTIALS is not set."
    exit 1
fi

echo "Using project: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER_NAME"



for BUCKET_NAME in "gs://$RAW_BUCKET" "gs://$CODE_BUCKET"; do
    echo "Verifying bucket $BUCKET_NAME..."
    if ! gsutil ls "$BUCKET_NAME" &>/dev/null; then
        echo "Creating bucket $BUCKET_NAME..."
        gsutil mb -l "$REGION" "$BUCKET_NAME"
        gsutil uniformbucketlevelaccess set on "$BUCKET_NAME"
    else
        echo "Bucket $BUCKET_NAME already exists. Activating uniform access..."
        gsutil uniformbucketlevelaccess set on "$BUCKET_NAME"
    fi

    echo "Grant necessary permissions to the Service Account..."
    gsutil iam ch "serviceAccount:$SERVICE_ACCOUNT:roles/storage.objectAdmin" "$BUCKET_NAME"
done


# Create cluster Dataproc
echo "Creating cluster Dataproc $CLUSTER_NAME..."
gcloud dataproc clusters create "$CLUSTER_NAME" \
    --region="$REGION_CLUSTER" \
    --subnet="default" \
    --single-node \
    --enable-component-gateway \
    --image-version="$IMAGE_VERSION" \
    --master-machine-type="$MACHINE_TYPE" \
    --master-boot-disk-size="$BOOT_DISK_SIZE" \
    --max-idle=300s \
    --no-address \
    --service-account=$SERVICE_ACCOUNT \
    --bucket=$RAW_BUCKET # "$(echo $RAW_BUCKET | sed 's|gs://||')"


# Identify logs bucket
echo "Detecting logs bucket..."
CONFIG_BUCKET=$(gcloud dataproc clusters describe "$CLUSTER_NAME" --region="$REGION_CLUSTER" --format="get(config.configBucket)")
echo "Logs Bucket detected: $CONFIG_BUCKET"

# Give access to your user to show cluster logs
echo "Asigning read perms user to $USER_EMAIL logs bucket..."
gsutil iam ch "user:$USER_EMAIL:roles/storage.objectViewer" "gs://$CONFIG_BUCKET"


# Run job PySpark
echo "Sending job Spark to Dataproc..."

# Run job PySpark
echo "Sending job Spark to Dataproc..."
gcloud dataproc jobs submit pyspark "$SPARK_JOB" \
  --cluster="$CLUSTER_NAME" \
  --region="$REGION_CLUSTER" \
  -- \
  --project-id="$PROJECT_ID" \
  --bq-dataset="$BQ_DATASET" \
  --bq-table-dim="$BQ_TABLE_DIM" \
  --bq-table-fact="$BQ_TABLE_FACT" \
  --raw-bucket="$RAW_BUCKET" \
  --parquet-bucket="$PARQUET_BUCKET"


# Delete cluste
echo "Deleting clúster Dataproc..."
gcloud dataproc clusters delete "$CLUSTER_NAME" --region="$REGION_CLUSTER" --quiet

echo "Process finished."