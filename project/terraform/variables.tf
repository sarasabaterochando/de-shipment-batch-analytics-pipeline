# =========================
# PROJECT / PROVIDER
# =========================
variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Default region for GCP resources"
  type        = string
}

# =========================
# LOCATIONS
# =========================
variable "gcs_location" {
  description = "Location for GCS buckets"
  type        = string
}

variable "bq_location" {
  description = "Location for BigQuery datasets"
  type        = string
}

# =========================
# GCS BUCKET SETTINGS
# =========================
variable "gcs_storage_class" {
  description = "Storage class for GCS buckets"
  type        = string
}

variable "gcs_bucket_raw_name" {
  description = "Suffix for raw data bucket name"
  type        = string
}

variable "gcs_bucket_code_name" {
  description = "Suffix for processing code bucket name"
  type        = string
}

variable "gcs_bucket_parquet_name" {
  description = "Suffix for processing code bucket name"
  type        = string
}

# =========================
# BIGQUERY
# =========================
variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  type        = string
}
