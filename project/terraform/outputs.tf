# terraform/outputs.tf
output "raw_bucket_name" {
  description = "Name of the raw data bucket"
  value       = google_storage_bucket.raw_batch_data.name
}

output "parquet_bucket_name" {
  description = "Name of the parquet data bucket"
  value       = google_storage_bucket.parquet_data.name
}

output "code_bucket_name" {
  description = "Name of the processing code bucket"
  value       = google_storage_bucket.processing_code.name
}

output "bq_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.batch_quality_dataset.dataset_id
}