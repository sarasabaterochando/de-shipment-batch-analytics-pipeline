import re
from pyspark.sql import SparkSession
from pyspark.sql.types import (
        StructField, StringType, FloatType, TimestampType, DoubleType, IntegerType
)
from pyspark.sql.functions import to_timestamp
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from google.cloud import storage
import os
import pandas as pd
from pyspark.sql.types import StructType
from functools import reduce
import logging
from functools import wraps
import argparse


spark = SparkSession.builder \
    .appName('production_batch_processor') \
    .getOrCreate()



logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

'''
# variables
dim_table_name = os.environ["BQ_TABLE_DIM"]
fact_table_name = os.environ["BQ_TABLE_FACT"]
dataset = os.environ["BQ_DATASET"]
project = os.environ["PROJECT_ID"]
bucket_name_raw = os.environ["RAW_BUCKET"]
bucket_name_parquet = os.environ["PARQUET_BUCKET"]
'''
today_date = datetime.today().strftime('%Y-%m-%d')
folder_prefix = f'ini/{today_date}/'

# Creates the dataframe schemas
schema_dim = StructType([
        StructField("shipment_batch_ID", StringType(), True),
        StructField("dispatch_date", TimestampType(), True),
        StructField("dispatch_time", StringType(), True),
        StructField("completion_date", TimestampType(), True),
        StructField("completion_time", StringType(), True),
        StructField("origin_facility_ID", StringType(), True),
        StructField("shipment_category", StringType(), True),
        StructField("handling_class", StringType(), True),
        StructField("remarks", StringType(), True),
        StructField("creation_data", TimestampType(), True)
    ])

schema_fact = StructType([
        StructField("shipment_batch_ID", StringType(), True),
        StructField("package_class", StringType(), True),
        StructField("total_weight_kg", FloatType(), True),
        StructField("load_percentage_bp", IntegerType(), True),
        StructField("package_count", IntegerType(), True),
        StructField("routing_rules", StringType(), True),
        StructField("destination_hubs", StringType(), True),
    ])




def parse_args():
    """ Accept the vars from the sh script """
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--bq-dataset', required=True)
    parser.add_argument('--bq-table-dim', required=True)
    parser.add_argument('--bq-table-fact', required=True)
    parser.add_argument('--raw-bucket', required=True)
    parser.add_argument('--parquet-bucket', required=True)
    return parser.parse_args()



def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Entering '{func.__name__}' with args={args} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Exiting '{func.__name__}' result={result}")
            return result
        except Exception as e:
            logger.error(f"Error in '{func.__name__}': {e}", exc_info=True)
            raise

    return wrapper


@log_function
def read_gcs_text(file_path):
    """ Read GCS text file """
    bucket_name_edited = file_path.replace("gs://", "").split("/")[0]
    blob_name = "/".join(file_path.replace("gs://", "").split("/")[1:])

    client = storage.Client()
    bucket = client.bucket(bucket_name_edited)
    blob = bucket.blob(blob_name)

    content = blob.download_as_text(encoding='latin-1')

    return content


@log_function
def parse_date(date_str):
    """ Parse date """
    if date_str and date_str.strip():
        try:
            return pd.to_datetime(date_str.strip(), format='%d/%m/%Y').to_pydatetime()
        except Exception as e:
            print(f'Date parse error {date_str}: {e}')
            return None
    return None


@log_function
def parse_time(time_str):
    """ Parse  time """
    if time_str and time_str.strip():
        try:
            time = pd.to_datetime(time_str.strip(), format="%H%M%S").time()
            return time.strftime('%H:%M:%S')
        except Exception as e:
            logger.error(f'Time parse error {time_str}:{e}')
            return None
    return None


@log_function
def create_dim_dict(principal_data):
    """  creates the dictionary with the fact data  """
    dict_dim = {
        "shipment_batch_ID": str(principal_data.get("ShipmentBatchID") or ""),
        "dispatch_date": parse_date(principal_data.get('DispatchDate') or principal_data.get('Date')),
        "dispatch_time": parse_time(principal_data.get('DispatchTime') or ""),
        "completion_date": parse_date(principal_data.get('CompletionDate') or principal_data.get('Date')),
        "completion_time": parse_time(principal_data.get("CompletionTime") or ""),
        "origin_facility_ID": str(principal_data.get("OriginFacilityID") or ""),
        "shipment_category": str(principal_data.get("ShipmentCategory") or ""),
        "handling_class": str(principal_data.get("HandlingClass") or ""),
        "remarks": str(principal_data.get("Remarks") or ""),
        "creation_data": datetime.now()
    }
    return dict_dim


@log_function
def create_fact_dict(package_blocks, id_dim):
    """ Creates the fact dictionary with several rows"""
    fact_rows = []
    for block in package_blocks:
        info = dict(re.findall(r"(\w+)=([^\n]*)", block))

        total_weight_kg = float(info.get("total_weight_kg", "0") or 0) / 1000
        package_count = int(info.get("package_count", "0") or 0)
        load_percentage_bp = int(info.get("load_percentage_bp", "0") or 0)
        destination_hubs = info["destination_hubs"] if info.get("destination_hubs") else ""

        fact_rows.append({
                "shipment_batch_ID": id_dim,        
                "package_class": info.get("package_class") or "",
                "total_weight_kg": total_weight_kg or 0.0,
                "package_count": package_count or 0,
                "load_percentage_bp": load_percentage_bp or 0,
                "routing_rules": info.get("routing_rules") or "",
                "destination_hubs": destination_hubs or ""
        })
    print('check the dict')
    print(fact_rows)

    return fact_rows


@log_function
def process_file(path_gcs):
    content = read_gcs_text(path_gcs)
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    principal_match = re.search(
        r"\[SHIPMENT_BATCH\](.*?)(?=\n\[PACKAGE_TYPE|\Z)",
        content,
        re.DOTALL
    )
    principal_data = dict(
        re.findall(r"(\w+)=([^\n]*)", principal_match.group(1))
    ) if principal_match else {}

    package_blocks = re.findall(
        r"\[PACKAGE_TYPE_\d+\]\s*(.*?)(?=\n\s*\[PACKAGE_TYPE_\d+\]|\Z)",
        content,
        re.DOTALL
    )

    logger.info(f"PACKAGE_TYPE blocks found: {len(package_blocks)}")
    
    # Creates the dicts
    dim_dict = create_dim_dict(principal_data)    
    fact_dict = create_fact_dict(package_blocks, dim_dict["shipment_batch_ID"])
    
    # Creates the dataframes
    df_dim = spark.createDataFrame([dim_dict], schema_dim)
    df_fact = spark.createDataFrame(fact_dict, schema_fact)
    
    return df_dim, df_fact


@log_function
def change_date_format_columns(df_result):     
    """ Normalize the date columns in df"""   
    df_result = (
        df_result
        .withColumn("dispatch_date", to_timestamp("dispatch_date", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("completion_date", to_timestamp("completion_date", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("creation_data", to_timestamp("creation_data", "yyyy-MM-dd HH:mm:ss"))
    )
    return df_result


@log_function
def upload_to_bigquery(type_upload, table, dataset, project, bucket_name_parquet):
    """ load into bigquery. table "dim" or "fact" """
    spark.read.parquet(f"gs://{bucket_name_parquet}/parquet/{today_date}/{type_upload}/") \
        .write.format("bigquery") \
        .option("table", f"{project}.{dataset}.{table}") \
        .mode("append") \
        .save()
    print("Rows inserted in BigQuery succesfully")


@log_function
def upload_to_parquet(df, type_upload, bucket_name_parquet):
    """ Uploads the dataframe to a bucket in GCS. Table "dim" or "fact" """
    df \
        .write \
        .mode("append") \
        .parquet(f"gs://{bucket_name_parquet}/parquet/{today_date}/{type_upload}/")

    print("Parquet file uploaded succesfully to GCS")



if __name__ == "__main__":

    # Vars from the args in sh script
    args = parse_args()
    dim_table_name = args.bq_table_dim
    fact_table_name = args.bq_table_fact
    dataset = args.bq_dataset
    project = args.project_id
    bucket_name_raw = args.raw_bucket
    bucket_name_parquet = args.parquet_bucket

    spark.conf.set('temporaryGcsBucket', bucket_name_raw)
   
    # Create the dataframe with the schemas
    df_fact_final = spark.createDataFrame([], schema_fact)
    df_dim_final = spark.createDataFrame([], schema_dim)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name_raw)

    blobs = bucket.list_blobs(prefix=folder_prefix)

    for blob in blobs:
        if not blob.name.endswith("/"): 
            try:
                path_gcs = f"{bucket_name_raw}/{blob.name}"
                print(f"Processing file: {path_gcs}")

                df_dim, df_fact = process_file(path_gcs)

                df_dim_final = df_dim_final.unionByName(df_dim)
                df_fact_final = df_fact_final.unionByName(df_fact)

            except Exception as e:
                print(f"Error: {e} in file {path_gcs}")

    # Check the data uploading is correct
    print("Show the dim 5 first rows")
    df_dim_final.show(5, truncate=False)
    print("Show the fact 5 first rows")
    df_fact_final.show(5, truncate=False)

    # Clean the data
    df_dim_final = change_date_format_columns(df_dim_final)
   
    print(f'\nRow dim number: {df_dim_final.count()}\nRow fact number: {df_fact_final.count()}')

    upload_to_parquet(df_dim_final, "dim", bucket_name_parquet)
    upload_to_parquet(df_fact_final, "fact", bucket_name_parquet)
    
    upload_to_bigquery("dim", dim_table_name, dataset, project, bucket_name_parquet)
    upload_to_bigquery("fact", fact_table_name, dataset, project, bucket_name_parquet)

    print('Process finished')