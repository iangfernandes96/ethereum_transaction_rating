import pytest
import respx
from httpx import Response
from src.alchemy import AlchemyClient


@pytest.fixture
def alchemy_client():
    return AlchemyClient()


@pytest.mark.asyncio
@respx.mock
async def test_get_transaction(alchemy_client):
    transaction_hash = "0x123"
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "hash": transaction_hash,
            "blockNumber": "0x5bad55",
            "from": "0xaddress1",
            "to": "0xaddress2",
            # Add other transaction details here
        },
    }

    respx.post(f"{alchemy_client.base_url}").mock(
        return_value=Response(200, json=mock_response)
    )

    result = await alchemy_client.get_transaction(transaction_hash)
    assert result is not None
    assert result["hash"] == transaction_hash


@pytest.mark.asyncio
@respx.mock
async def test_get_block_by_number(alchemy_client):
    block_number = "0x5bad55"
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "number": block_number,
            "transactions": [],
            # Add other block details here
        },
    }

    respx.post(f"{alchemy_client.base_url}").mock(
        return_value=Response(200, json=mock_response)
    )

    result = await alchemy_client.get_block_by_number(block_number)
    assert result is not None
    assert result["number"] == block_number


@pytest.mark.asyncio
@respx.mock
async def test_get_latest_blocks(alchemy_client):
    mock_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "number": "0x5bad56",
            "transactions": [],
            # Add other block details here
        },
    }

    respx.post(f"{alchemy_client.base_url}").mock(
        return_value=Response(200, json=mock_response)
    )

    result = await alchemy_client.get_latest_blocks()
    assert result is not None
    assert result["number"] == "0x5bad56"
