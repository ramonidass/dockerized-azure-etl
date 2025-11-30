import pytest
from unittest.mock import AsyncMock, patch
from src.extract import get_wallet_activity
from src.schemas.schema import WalletActivity


@pytest.mark.asyncio
async def test_get_wallet_activity_success():
    mock_client = AsyncMock()
    mock_client.get.return_value = {
        "data": [
            {
                "height": 123,
                "confirmations": 10,
                "tx_hash": "abc",
                "sat_activity": {"kind": "increase", "amount": "100"},
            }
        ],
        "last_updated": {"block_hash": "hash", "block_height": 456},
        "next_cursor": "cursor",
    }

    result = await get_wallet_activity(mock_client, "test_wallet")

    assert isinstance(result, dict)
    assert "data" in result
    # Validate with schema
    WalletActivity(**result)


@pytest.mark.asyncio
async def test_get_wallet_activity_failure():
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("API error")

    result = await get_wallet_activity(mock_client, "test_wallet")

    assert result == {}
