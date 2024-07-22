from datetime import datetime, UTC
from fastapi_utils.tasks import repeat_every
from .alchemy import AlchemyClient
from .config import REFRESH_TXN_INTERVAL
from .redis_client import TransactionRedisManager


alchemy_client = AlchemyClient()
txns_redis_client = TransactionRedisManager()


def str_to_hex(block_str: str) -> int:
    return int(block_str, 16)


def get_block_age(block_timestamp: int) -> int:
    return (
        datetime.now(UTC) - datetime.fromtimestamp(block_timestamp, UTC)
    ).days  # noqa


def get_trust_rating(txn_hash: str, block_number: str) -> int:
    return (str_to_hex(txn_hash) + str_to_hex(block_number)) % 5 + 1


@repeat_every(seconds=REFRESH_TXN_INTERVAL)
async def refresh_latest_hashes():
    """
    To periodically refresh the latest hashes in the background."""
    block = await alchemy_client.get_latest_blocks()
    transactions = block.get("transactions") if block else []
    old_hashes = await txns_redis_client.get_latest_hashes()
    if old_hashes:
        await txns_redis_client.set_old_hashes(old_hashes)
    await txns_redis_client.set_latest_hashes(transactions)
