from pydantic import BaseModel
from typing import List


class SatActivity(BaseModel):
    kind: str
    amount: str


class Transaction(BaseModel):
    height: int
    confirmations: int
    tx_hash: str
    sat_activity: SatActivity


class LastUpdated(BaseModel):
    block_hash: str
    block_height: int


class WalletActivity(BaseModel):
    data: List[Transaction]
    last_updated: LastUpdated
    next_cursor: str
