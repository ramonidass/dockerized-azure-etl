import polars as pl
import io
from pathlib import Path
from typing import List, Dict, Any
from azure.storage.blob import BlobServiceClient
from .utils.logger import get_logger
from .schemas.schema import WalletActivity
from .settings import settings

logger = get_logger(__name__)


def process_and_save_wallet_data(
    wallet_data: Dict[str, Any], output_path: str = "data/wallet_activity.parquet"
) -> None:
    """
    Processes wallet activity data, validates with Pydantic, creates Polars DataFrame, and saves to local Parquet.

    Args:
        wallet_data: Dict with wallet as key and activity dict as value.
        output_path: Path to save the Parquet file.
    """
    all_rows: List[Dict[str, Any]] = []

    for wallet, activity in wallet_data.items():
        if not activity:
            logger.warning(f"No activity data for {wallet}.")
            continue

        try:
            validated_activity = WalletActivity(**activity)
            logger.info(
                f"Successfully validated activity for {wallet}: {len(validated_activity.data)} transactions"
            )
        except Exception as e:
            logger.error(f"Validation failed for {wallet}: {e}")
            continue

        # Flatten data for DataFrame
        for tx in validated_activity.data:
            row = {
                "wallet": wallet,
                "height": tx.height,
                "confirmations": tx.confirmations,
                "tx_hash": tx.tx_hash,
                "sat_kind": tx.sat_activity.kind,
                "sat_amount": tx.sat_activity.amount,
            }
            all_rows.append(row)

    if all_rows:
        df = pl.DataFrame(all_rows)

        if settings.azure_storage_account and settings.azure_storage_key and settings.azure_container:
            buffer = io.BytesIO()
            df.write_parquet(buffer)
            buffer.seek(0)
            blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.azure_storage_account}.blob.core.windows.net",
                credential=settings.azure_storage_key,
            )
            blob_client = blob_service_client.get_blob_client(
                container=settings.azure_container, blob=Path(output_path).name
            )
            blob_client.upload_blob(buffer, overwrite=True)
            logger.info(f"Uploaded {len(all_rows)} transactions to Azure Blob: {settings.azure_container}/{Path(output_path).name}")

        # Default to local
        else:
            data_dir = Path(output_path).parent
            data_dir.mkdir(exist_ok=True)
            df.write_parquet(output_path)
            logger.info(f"Saved {len(all_rows)} transactions locally to {output_path}")
    else:
        logger.warning("No data to save.")
