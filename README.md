# ETL to BigQuery with Airflow + Docker + GCP

This project demonstrates an end-to-end ETL pipeline using Apache Airflow, Docker, and Google Cloud Platform (GCP). We extract data from a local CSV file, upload it to Google Cloud Storage (GCS), and load it into BigQuery.

---

##  Prerequisites

### 1. GCP Setup

- Create a GCP project
- Enable the following APIs:
  - BigQuery API
  - Cloud Storage API
  - IAM API
- Create a service account:
  - Assign roles:
    - BigQuery Admin
    - Storage Admin
  - Generate a JSON key and download it

### 2. Local Setup

- Clone the repo:
```bash
git clone <your-repo-url>
cd airflow_gcp_etl_postgres
```
- Place your service account JSON key in the root directory
- Create a folder named `keys` and move the key there
```bash
mkdir keys
mv <your-key-file>.json keys/
```

- Add your GCP project ID and bucket name in the `.env` file.

### 3. Airflow Initialization

```bash
docker compose up airflow-init
```

### 4. Start Airflow

```bash
docker compose up
```

---

##  Project Structure

```
.
├── dags/
│   └── etl_to_bq.py
├── data/
│   └── raw_products.csv
├── keys/
│   └── your-service-account.json
├── .env
├── docker-compose.yaml
└── README.md
```

---

## DAG Overview

### DAG: `etl_to_bq`

#### Tasks:
1. `extract_transform`: Reads `raw_products.csv`, cleans data, and saves as `products_cleaned.csv`
2. `upload_to_gcs`: Uploads `products_cleaned.csv` to GCS bucket
3. `load_to_bigquery`: Loads GCS file into BigQuery table

---

## Key Code Snippets

### LocalFilesystemToGCSOperator

```python
upload_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_to_gcs',
    src='products_cleaned.csv',
    dst='products_cleaned.csv',
    bucket='my-airflow-etl-bucket',
    gcp_conn_id='google_cloud_default',
)
```

### BigQueryInsertJobOperator

```python
load_to_bq = BigQueryInsertJobOperator(
    task_id="load_to_bigquery",
    configuration={
        "load": {
            "sourceUris": ["gs://my-airflow-etl-bucket/products_cleaned.csv"],
            "destinationTable": {
                "projectId": "your-gcp-project-id",
                "datasetId": "demo_etl",
                "tableId": "products_cleaned",
            },
            "sourceFormat": "CSV",
            "autodetect": True,
            "skipLeadingRows": 1,
            "writeDisposition": "WRITE_TRUNCATE",
        }
    },
    location="US",
    gcp_conn_id="google_cloud_default",
)
```

---

## 🧪 Testing

1. Visit `http://localhost:8080`
2. Trigger `etl_to_bq` DAG manually
3. Confirm file uploads in GCS and rows appear in BigQuery

---

## Notes

- Set `AIRFLOW__CORE__LOAD_EXAMPLES=False` in `.env` to disable example DAGs
- Mount key volume in `docker-compose.yaml`:

```yaml
volumes:
  - ./keys:/keys
```

---

## Success Screenshots

- DAG Success in Airflow UI
- GCS Bucket File
- BigQuery Table Data

---

## Credits

Built with ❤️ using Apache Airflow, GCP, and Docker by Aish.
