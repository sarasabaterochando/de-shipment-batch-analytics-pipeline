import os
from google.cloud import storage
from pathlib import Path
from datetime import datetime
import json

"""
Prerequisites:
1. pip install pandas pyarrow google-cloud-storage
"""

# GCS bucket configuration
BUCKET_NAME = os.environ["RAW_BUCKET"]
PROCESSED_BLOB_NAME = "processed/processed_files.json"


def update_processed_files(new_files, processed_files, processed_blob, processed_blob_name):
    """
    Updates the processed_files.json state file in Google Cloud Storage.

    Args:
        new_files (list): List of newly processed file names.
        processed_files (list): List of already processed files.
        processed_blob (Blob): GCS blob for the state file.
        processed_blob_name (str): Name of the state file blob.
    """
    if new_files:
        processed_files.extend(new_files)
        updated_state = json.dumps(
            {"processed_files": processed_files},
            indent=2
        )
        try:
            processed_blob.upload_from_string(
                updated_state,
                content_type="application/json"
            )
            print(f"State file successfully updated: {processed_blob_name}")
        except Exception as e:
            print(f"Failed to upload state file: {e}")
    else:
        print("No new files detected. State file was not updated.")


def upload_to_gcs():
    """
    Uploads local files to Google Cloud Storage if they do not already exist.
    Keeps track of processed files using a JSON state file.
    """

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    processed_blob = bucket.blob(PROCESSED_BLOB_NAME)

    # 1. Load processed files state
    processed_files = []
    try:
        if processed_blob.exists():
            content = processed_blob.download_as_text()
            processed_files = json.loads(content).get("processed_files", [])
    except Exception as e:
        print(f"Failed to read state file: {e}")

    new_files = []

    # 2. Iterate over local directory files
    local_path = Path("/opt/airflow/ini_files") 
    print(f"Scanning local directory: {local_path}")
    
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    for file_path in local_path.iterdir():
        if not file_path.is_file():
            continue

        destination_blob_name = f'ini/{today_date}/{file_path.name}'
        blob = bucket.blob(destination_blob_name)

        if file_path.name in processed_files:
            print(f"{file_path.name} has already been processed. Skipping.")
            continue

        try:
            if blob.exists():
                print(f"{file_path.name} already exists in GCS. Skipping upload.")
                continue

            blob.upload_from_filename(str(file_path))
            print(f"Uploaded {file_path.name} to {destination_blob_name}.")
            new_files.append(file_path.name)

        except Exception as e:
            print(f"Failed to upload {file_path.name} to GCS. Error: {e}")

    # 3. Update processed files state in GCS
    update_processed_files(
        new_files,
        processed_files,
        processed_blob,
        PROCESSED_BLOB_NAME
    )


if __name__ == "__main__":
    try:
        upload_to_gcs()
    except Exception as error:
        print(f"Unexpected error during execution: {error}")

