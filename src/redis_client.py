from typing import Any, Optional
from redis import Redis
import orjson as json
from .config import (
    REDIS_PORT,
    REDIS_HOST,
    RATED_BLOCK_REDIS_KEY,
    LATEST_TXNS_REDIS_KEY,
    OLD_TXNS_REDIS_KEY,
    LATEST_TXNS_TTL,
)


class RedisClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._client = Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        return self._client.get(key)

    async def setex(self, key: str, ttl: int, value: Any) -> None:
        self._client.setex(key, ttl, value)

    async def set(self, key: str, value: Any) -> None:
        self._client.set(key, value)

    async def delete(self, key: str) -> None:
        self._client.delete(key)


class TransactionRedisManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._client = RedisClient()
        self._rated_block_key = RATED_BLOCK_REDIS_KEY
        self._latest_txns_key = LATEST_TXNS_REDIS_KEY
        self._old_txns_key = OLD_TXNS_REDIS_KEY

    async def get_rated_txn(self, key: str) -> Optional[Any]:
        """
        Fetches an already rated transaction from Redis, if it exists"""
        return await self._client.get(f"{self._rated_block_key}:{key}")

    async def set_rated_block(self, key: str, value: Any) -> None:
        """
        Caches a rated transaction in Redis"""
        await self._client.set(f"{self._rated_block_key}:{key}", value)

    async def get_latest_hashes(self) -> Optional[Any]:
        """
        Fetches the latest transaction hashes from Redis"""
        val = await self._client.get(self._latest_txns_key)
        return json.loads(val) if val else None

    async def set_latest_hashes(self, value: Any) -> None:
        """
        Caches the latest transaction hashes in Redis, with a TTL"""
        await self._client.setex(
            self._latest_txns_key, LATEST_TXNS_TTL, json.dumps(value)
        )
        print("Latest hashes set in Redis")

    async def get_old_hashes(self) -> Optional[Any]:
        """
        Fetches the old transaction hashes from Redis"""
        val = await self._client.get(self._old_txns_key)
        return json.loads(val) if val else None

    async def is_old_hash(self, key: str) -> bool:
        """
        Checks if a transaction hash is present in the
        list of old hashes."""
        old_hashes = await self.get_old_hashes()
        if old_hashes:
            print(f"Key in old hash: {key in old_hashes}")
        return key in old_hashes if old_hashes else False

    async def is_latest_hash(self, key: str) -> bool:
        """
        Checks if a transaction hash is present in the
        list of latest hashes."""
        latest_hashes = await self.get_latest_hashes()
        if latest_hashes:
            print(f"Key in latest hash: {key in latest_hashes}")
        return key in latest_hashes if latest_hashes else False

    async def set_old_hashes(self, value: Any) -> None:
        """
        Caches the old transaction hashes in Redis"""
        await self._client.set(self._old_txns_key, json.dumps(value))
