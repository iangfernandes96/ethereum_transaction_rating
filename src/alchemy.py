from typing import Optional, Any, Dict
from httpx import AsyncClient
from .config import ALCHEMY_API_KEY, ALCHEMY_ENDPOINT


class AlchemyClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, api_key: str = ALCHEMY_API_KEY, endpoint: str = ALCHEMY_ENDPOINT
    ):
        self.base_url = f"{endpoint}/{api_key}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.static_payload = {"id": 1, "jsonrpc": "2.0"}
        self.client = AsyncClient(headers=self.headers)

    async def _post_handler(
        self, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:  # noqa
        """
        Handles POST requests to the Alchemy API
        """
        response = await self.client.post(self.base_url, json=data)
        if response.status_code == 200:
            return response.json().get("result")
        return None

    async def get_transaction(
        self, transaction_hash: str
    ) -> Optional[Dict[str, Any]]:  # noqa
        """
        Fetches a transaction by its hash
        """
        data = {
            "method": "eth_getTransactionByHash",
            "params": [transaction_hash],
            **self.static_payload,
        }
        return await self._post_handler(data)

    async def get_block_by_number(
        self, block_number: str
    ) -> Optional[Dict[str, Any]]:  # noqa
        """
        Fetches a block by its number
        """
        data = {
            "method": "eth_getBlockByNumber",
            "params": [block_number, True],
            **self.static_payload,
        }
        return await self._post_handler(data)

    async def get_latest_blocks(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the latest block
        """
        data = {
            "method": "eth_getBlockByNumber",
            "params": ["latest", False],
            **self.static_payload,
        }
        return await self._post_handler(data)
