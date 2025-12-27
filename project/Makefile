SHELL := /bin/bash

.PHONY: help init plan apply destroy clean tfvars

# Colors to output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Show this help
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'


debug-env: ## Debug: show loaded environment variables
	@echo "$(BLUE)Debugging environment variables...$(NC)"
	@if [ ! -f airflow/config/config.env ]; then \
		echo "$(RED)❌ Error: airflow/config/config.env doesn't exist$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)File exists. Content:$(NC)"
	@cat airflow/config/config.env
	@echo ""
	@echo "$(GREEN)Loading variables:$(NC)"
	@set -a && . ./airflow/config/config.env && set +a && \
		echo "PROJECT_ID=$$PROJECT_ID" && \
		echo "REGION=$$REGION" && \
		echo "GCS_LOCATION=$$GCS_LOCATION" && \
		echo "BQ_LOCATION=$$BQ_LOCATION" && \
		echo "GCS_STORAGE_CLASS=$$GCS_STORAGE_CLASS" && \
		echo "BUCKET_RAW_SUFFIX=$$BUCKET_RAW_SUFFIX" && \
		echo "BUCKET_CODE_SUFFIX=$$GCS_BUCKET_CODE_SUFFIX" && \
		echo "GCS_BUCKET_PARQUET_SUFFIX=$$GCS_BUCKET_PARQUET_SUFFIX" && \
		echo "BQ_DATASET=$$BQ_DATASET"


tfvars: ## Generate terraform.tfvars from airflow/config/config.env
	@echo "$(GREEN)Generating terraform.tfvars...$(NC)"
	@if [ ! -f airflow/config/config.env ]; then \
		echo "$(RED)❌ Error: airflow/config/config.env doesn't exist$(NC)"; \
		exit 1; \
	fi
	@bash -c 'source ./airflow/config/config.env && \
		echo "project_id                = \"$$PROJECT_ID\"" > terraform/terraform.tfvars && \
		echo "region                    = \"$$REGION\"" >> terraform/terraform.tfvars && \
		echo "gcs_location              = \"$$GCS_LOCATION\"" >> terraform/terraform.tfvars && \
		echo "bq_location               = \"$$BQ_LOCATION\"" >> terraform/terraform.tfvars && \
		echo "gcs_storage_class         = \"$$GCS_STORAGE_CLASS\"" >> terraform/terraform.tfvars && \
		echo "gcs_bucket_raw_name     = \"$$RAW_BUCKET\"" >> terraform/terraform.tfvars && \
		echo "gcs_bucket_code_name    = \"$$CODE_BUCKET\"" >> terraform/terraform.tfvars && \
		echo "gcs_bucket_parquet_name = \"$$PARQUET_BUCKET\"" >> terraform/terraform.tfvars && \
		echo "bq_dataset_name           = \"$$BQ_DATASET\"" >> terraform/terraform.tfvars'
	@echo "$(GREEN)✅ terraform.tfvars generated$(NC)"


init: tfvars ## Initialize Terraform
	@cd terraform && terraform init

plan: tfvars ## View plan of changes
	@cd terraform && terraform plan

apply: tfvars ## Apply changes
	@cd terraform && terraform apply

destroy: tfvars ## Destroy terraform
	@cd terraform && terraform destroy

clean: ## Clean generated files
	@rm -f terraform/terraform.tfvars
	@rm 	-rf terraform/.terraform
	@rm -f terraform/*.tfstate*
	@echo "$(GREEN)✅ Archivos limpiados$(NC)"

create-bq-tables: ## Create tables in BigQuery
	@echo "Creating tables in BigQuery..."
	@python3 scripts/create_bq_tables.py
	@echo "Tables generated succesfully"

airflow-up: ## Start Airflow with docker-compose
	@echo "🚀 Starting Airflow..."
	chmod +x airflow/scripts/deploy_dataproc_job.sh
	@cd airflow && docker-compose up -d

airflow-down: ## Stop Airflow
	@echo "🛑 Stopping Airflow..."
	@cd airflow && docker-compose down

airflow-logs: ## Show Airflow logs
	@cd airflow && docker-compose logs -f

all: deploy airflow-up ## Deploy infrastructure and start Airflow