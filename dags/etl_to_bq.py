from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime
import pandas as pd
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator

def extract_and_clean():
    df = pd.read_csv('/opt/airflow/data/raw_products.csv')
    df_cleaned = df.dropna()
    df_cleaned.to_csv('/opt/airflow/data/products_cleaned.csv', index=False)

with DAG("etl_to_bq", start_date=datetime(2023,1,1), schedule="@once", catchup=False) as dag:

    extract_clean = PythonOperator(
        task_id="extract_and_clean",
        python_callable=extract_and_clean
    )

    upload_to_gcs = LocalFilesystemToGCSOperator(
    task_id="upload_to_gcs",
    src="/opt/airflow/data/products_cleaned.csv",  # path inside Airflow container
    dst="products_cleaned.csv",                    # file name in GCS bucket
    bucket="my-airflow-etl-bucket",                # your GCS bucket name
    gcp_conn_id="google_cloud_default",
    )

    load_to_bq = BigQueryInsertJobOperator(
        task_id="load_to_bigquery",
        configuration={
            "load": {
                "sourceUris": ["gs://my-airflow-etl-bucket/products_cleaned.csv"],  # You’ll update this
                "destinationTable": {
                    "projectId": "third-flare-464317-r8",
                    "datasetId": "demo_etl",
                    "tableId": "products_cleaned"
                },
                "sourceFormat": "CSV",
                "autodetect": True,
                "skipLeadingRows": 1,
                "writeDisposition": "WRITE_TRUNCATE"
            }
        },
        location="US",
        gcp_conn_id="google_cloud_default"
    )

    extract_clean >> upload_to_gcs >> load_to_bq

