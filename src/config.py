# Alchemy config
ALCHEMY_API_KEY = "6jAEJm8FzvaQDWwH7tKEUHaf6ABykPSp"
ALCHEMY_ENDPOINT = "https://eth-mainnet.g.alchemy.com/v2"
ETH_NETWORK = "eth-mainnet"

# Auth config
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = "YOUR_SECRET"


# Redis configuration
REDIS_HOST = "redis"
REDIS_PORT = 6379
RATED_BLOCK_REDIS_KEY = "rated_blocks"
LATEST_TXNS_REDIS_KEY = "latest_txns"
OLD_TXNS_REDIS_KEY = "old_txns"
LATEST_TXNS_TTL = 120   # seconds
REFRESH_TXN_INTERVAL = 60  # seconds

# FastAPI route configuration
USER_PREFIX = "/api/user"
TXN_PREFIX = "/api/transaction"
TOKEN_ENDPOINT = "/token"
LATEST_HASHES_ENDPOINT = "/latest-hashes"
OLD_HASHES_ENDPOINT = "/old-hashes"
RATING_ENDPOINT = "/rating"

# Transaction configuration
BLOCK_AGE_LIMIT_DAYS = 30
