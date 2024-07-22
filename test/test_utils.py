from datetime import datetime, timezone
from freezegun import freeze_time
from src.utils import str_to_hex, get_block_age, get_trust_rating


def test_str_to_hex():
    assert str_to_hex("0x1a") == 26
    assert str_to_hex("0xff") == 255
    assert str_to_hex("0x10") == 16


@freeze_time("2024-07-20")
def test_get_block_age():
    block_timestamp = (
        datetime(2024, 7, 18, tzinfo=timezone.utc)
        - datetime(1970, 1, 1, tzinfo=timezone.utc)
    ).total_seconds()
    assert get_block_age(block_timestamp) == 2  # type: ignore

    block_timestamp = (
        datetime(2024, 7, 19, tzinfo=timezone.utc)
        - datetime(1970, 1, 1, tzinfo=timezone.utc)
    ).total_seconds()
    assert get_block_age(block_timestamp) == 1  # type: ignore


def test_get_trust_rating():
    txn_hash = "0x1a"
    block_number = "0x10"
    assert get_trust_rating(txn_hash, block_number) == 3

    txn_hash = "0xff"
    block_number = "0x10"
    assert get_trust_rating(txn_hash, block_number) == 2
