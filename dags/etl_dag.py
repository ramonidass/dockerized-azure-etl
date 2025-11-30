from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.providers.docker.operators.docker import DockerOperator

default_args = {
    "owner": "data-eng",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "wallet_activity_etl",
    default_args=default_args,
    description="ETL pipeline for wallet activity data",
    schedule_interval="@daily",
    catchup=False,
)

etl_task = DockerOperator(
    task_id="run_etl",
    image="your-registry/databricks-etl:latest",  # Replace with your Docker image
    command=["python", "-m", "src.main"],
    environment={
        "KEY": Variable.get("api_key"),
        "BASE_URL": Variable.get("base_url"),
        "TETHER_WALLET": Variable.get("tether_wallet"),
        "BINANCE_WALLET": Variable.get("binance_wallet"),
        # Optional Azure Blob
        "AZURE_STORAGE_ACCOUNT": Variable.get("azure_storage_account", ""),
        "AZURE_STORAGE_KEY": Variable.get("azure_storage_key", ""),
        "AZURE_CONTAINER": Variable.get("azure_container", ""),
    },
    dag=dag,
)
