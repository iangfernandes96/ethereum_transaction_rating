from fastapi import APIRouter, Depends
from src.auth import get_current_user
from src.models import (
    LatestHashesResponse,
    RatingResponse,
    OldHashesResponse,
    User,
)
from src.redis_client import TransactionRedisManager
from src.alchemy import AlchemyClient
from src.exceptions import (
    TransactionNotFoundException,
    BlockNotFoundException,
    RestrictedAccessException,
)
from src.utils import get_block_age, str_to_hex, get_trust_rating
from src.config import (
    BLOCK_AGE_LIMIT_DAYS,
    RATING_ENDPOINT,
    LATEST_HASHES_ENDPOINT,
    OLD_HASHES_ENDPOINT,
)

txn_router = APIRouter()
txns_redis_client = TransactionRedisManager()
alchemy_client = AlchemyClient()


@txn_router.get(LATEST_HASHES_ENDPOINT, response_model=LatestHashesResponse)
async def latest_hashes(user: User = Depends(get_current_user)):
    # check if latest hashes are cached
    cached_hashes = await txns_redis_client.get_latest_hashes()
    if cached_hashes:
        return LatestHashesResponse(latest_transaction_hashes=cached_hashes)
    block = await alchemy_client.get_latest_blocks()
    transactions = block.get("transactions", []) if block else []
    if transactions:
        await txns_redis_client.set_latest_hashes(transactions)
    return LatestHashesResponse(latest_transaction_hashes=transactions)


@txn_router.get(RATING_ENDPOINT, response_model=RatingResponse)
async def get_safe_rating(
    transaction_hash: str, user: User = Depends(get_current_user)
) -> RatingResponse:
    # Check if block has been rated before
    cached_rating = await txns_redis_client.get_rated_txn(transaction_hash)
    if cached_rating:
        return RatingResponse(
            rating=int(cached_rating), transaction_hash=transaction_hash
        )
    is_paid_user = user.paid
    is_old_hash = await txns_redis_client.is_old_hash(transaction_hash)
    is_latest_hash = await txns_redis_client.is_latest_hash(transaction_hash)

    if not is_paid_user and is_latest_hash:
        raise RestrictedAccessException

    transaction = await alchemy_client.get_transaction(transaction_hash)
    if not transaction:
        raise TransactionNotFoundException

    block_number = transaction.get("blockNumber", "0")
    block = await alchemy_client.get_block_by_number(block_number)
    if not block:
        raise BlockNotFoundException

    block_timestamp = str_to_hex(block.get("timestamp", "0"))
    block_age_days = get_block_age(block_timestamp)

    if not is_paid_user:
        if not is_old_hash and block_age_days < BLOCK_AGE_LIMIT_DAYS:
            raise RestrictedAccessException

    txn_hash = transaction.get("hash", "")

    trust_rating = get_trust_rating(txn_hash, block_number)

    # Cache this rated block in Redis
    await txns_redis_client.set_rated_block(transaction_hash, trust_rating)

    return RatingResponse(
        rating=trust_rating, transaction_hash=transaction["hash"]
    )  # noqa


@txn_router.get(OLD_HASHES_ENDPOINT, response_model=OldHashesResponse)
async def old_hashes(user: User = Depends(get_current_user)):
    cached_hashes = await txns_redis_client.get_old_hashes()
    if cached_hashes:
        return OldHashesResponse(old_transaction_hashes=cached_hashes)
    raise TransactionNotFoundException
