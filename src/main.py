from contextlib import asynccontextmanager
from fastapi import FastAPI
from .alchemy import AlchemyClient
from .redis_client import TransactionRedisManager
from .users import UserDB
from .utils import refresh_latest_hashes
from .routers.user import user_router
from .routers.transactions import txn_router
from .config import USER_PREFIX, TXN_PREFIX

alchemy_client = AlchemyClient()
txns_redis_client = TransactionRedisManager()
user_db = UserDB()


@asynccontextmanager
async def lifespan_task(app: FastAPI):
    """
    To refresh the latest hashes in the background
    """
    await refresh_latest_hashes()
    yield


app = FastAPI(lifespan=lifespan_task)

app.include_router(user_router, prefix=USER_PREFIX)
app.include_router(txn_router, prefix=TXN_PREFIX)
