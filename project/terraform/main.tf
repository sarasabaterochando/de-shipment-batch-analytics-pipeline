terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.16.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# =========================
# GCS BUCKET - RAW DATA
# =========================
resource "google_storage_bucket" "raw_batch_data" {
  name          = var.gcs_bucket_raw_name
  location      = var.gcs_location
  storage_class = var.gcs_storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }

  labels = {
    environment = "portfolio"
    layer       = "raw"
    owner       = "data"
  }
}

# =========================
# GCS BUCKET - PARQUET DATA
# =========================
resource "google_storage_bucket" "parquet_data" {
  name          = var.gcs_bucket_parquet_name
  location      = var.gcs_location
  storage_class = var.gcs_storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    environment = "portfolio"
    layer       = "processed"
    owner       = "data"
  }
}

# =========================
# GCS BUCKET - PROCESSING CODE
# =========================
resource "google_storage_bucket" "processing_code" {
  name          = var.gcs_bucket_code_name
  location      = var.gcs_location
  storage_class = var.gcs_storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    environment = "portfolio"
    layer       = "code"
    owner       = "data"
  }
}

# =========================
# BIGQUERY DATASET
# =========================
resource "google_bigquery_dataset" "batch_quality_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.bq_location

  labels = {
    environment = "portfolio"
    domain      = "batch_quality"
  }
}

# =========================
# UPLOAD SPARK SCRIPT TO CODE BUCKET
# =========================
resource "google_storage_bucket_object" "spark_job_script" {
  name   = "scripts/spark/gcs_to_bigquery_upload.py"
  bucket = google_storage_bucket.processing_code.name
  source = "${path.module}/../scripts/spark/gcs_to_bigquery_upload.py"
  
  # Force re-upload if file changes
  detect_md5hash = "different"
}