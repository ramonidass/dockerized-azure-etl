
# ETL Async API to Databricks Medallion

This project implements a ETL pipeline for fetching Bitcoin wallet activity data asynchronously, validating with Pydantic, and processing in Databricks. Uses Airflow for orchestration and Azure Blob Storage.

## Architecture Overview
- **Extract**: Async API calls to API for wallet transactions.
- **Transform**: Pydantic validation, flatten to Polars DataFrame.
- **Load**: Save to Parquet (local or Azure Blob).
- **Process**: Databricks and dbt for medallion layers (Bronze/Silver/Gold).

## Project Structure
```
├── dags/                 # Airflow DAGs
├── src/                  # ETL code
│   ├── main.py          # Entry point
│   ├── extract.py       # API extraction
│   ├── load.py          # Data loading
│   ├── schemas/         # Pydantic models
│   └── settings.py      # Config
├── tests/               # Unit tests
├── data/                # Local Parquet output
├── docker-compose.yml   # Local Airflow
└── Dockerfile           # ETL container
```

## Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local testing)
- Databricks Community account (free at https://community.cloud.databricks.com/)
- Azure cloud account free

## Setup Steps

### 1. Install Dependencies
```bash
uv sync
```

### 2. Build Docker Image
```bash
docker build -t databricks-etl:latest .
```

### 3. Start Local Airflow
```bash
docker-compose up -d
```
- Access Airflow UI at http://localhost:8080 (user: admin, pass: admin)

### 4. Set Airflow Variables
In Airflow UI > Admin > Variables, add:
- `api_key`: API key
- `base_url`: https://xbt-mainnet.gomaestro-api.org/v0/addresses
- `tether_wallet`: wallet address
- `binance_wallet`: wallet address

#### Azure Blob Storage
If you have an Azure Storage Account:
1. Go to [Azure Portal](https://portal.azure.com) > Search "Storage accounts" > Select your account.
2. **Storage Account Name**: Overview tab > Copy "Storage account name".
3. **Storage Account Key**: Left menu > "Access keys" > Under "key1" > Copy "Key".
4. **Container Name**: Left menu > "Containers" > Select your container > Copy name.

Add to variables:
```.env
- `azure_storage_account`: <account_name>
- `azure_storage_key`: <key>
- `azure_container`: <container_name>

```

### 5. Run the DAG
- Enable the `wallet_activity_etl` DAG.
- Trigger manually or wait for daily schedule.
- Check logs for Parquet saved to `data/wallet_activity.parquet`.

### 6. Upload to Databricks Community
- If local: Download `data/wallet_activity.parquet` and upload to Databricks Community (Data > Upload File).
- If Azure: Access directly in Databricks (add Azure storage mount or use `spark.read.parquet("wasbs://<container>@<account>.blob.core.windows.net/wallet_activity.parquet")`).
- Create a notebook to read and process:
  ```python
  df = spark.read.parquet("/FileStore/wallet_activity.parquet")  # Or Azure path
  df.display()
  # Bronze: df.write.format("delta").save("/delta/bronze")
  # Silver: Clean data
  # Gold: Aggregations
  ```
- Implement Bronze/Silver/Gold layers manually.
