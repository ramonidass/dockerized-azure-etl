from src.utils.logger import get_logger
from typing import Dict, Any
import httpx
from src.utils.client import AsyncAPIClient
from .settings import settings

logger = get_logger(__name__)


async def get_wallet_activity(
    api_client: AsyncAPIClient, wallet_id: str
) -> Dict[str, Any]:
    """
    Fetches wallet activity from the API.
    """
    endpoint = f"/{wallet_id}/activity"
    try:
        response = await api_client.get(endpoint)
        return response if isinstance(response, dict) else {}
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch wallet {wallet_id}: {e}")
        return {}
    except httpx.RequestError as e:
        logger.error(f"Network error for wallet {wallet_id}: {e}")
        return {}
