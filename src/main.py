import asyncio
from .settings import settings
from .utils.client import AsyncAPIClient
from .extract import get_wallet_activity
from .load import process_and_save_wallet_data
from .utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """
    Initializes the API client and fetches wallet activity for multiple addresses.
    """
    api_client = AsyncAPIClient(
        base_url=settings.base_url,
        api_key=settings.key,
        auth_header="api-key",
        auth_prefix="",
    )
    async with api_client:
        wallets = [settings.tether_wallet, settings.binance_wallet]
        logger.info(f"Fetching activity for wallets: {wallets}")
        tasks = [
            get_wallet_activity(api_client=api_client, wallet_id=wallet)
            for wallet in wallets
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        wallet_data = {}
        for wallet, result in zip(wallets, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch activity for {wallet}: {result}")
            else:
                wallet_data[wallet] = result

        process_and_save_wallet_data(wallet_data, output_path="data/wallet_activity.parquet")


if __name__ == "__main__":
    asyncio.run(main())
