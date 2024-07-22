from pydantic import BaseModel


class Transaction(BaseModel):
    hash: str
    block_number: int


class TokenData(BaseModel):
    username: str = ""


class User(BaseModel):
    username: str
    password: str
    paid: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LatestHashesResponse(BaseModel):
    latest_transaction_hashes: list[str]


class OldHashesResponse(BaseModel):
    old_transaction_hashes: list[str]


class RatingResponse(BaseModel):
    rating: int
    transaction_hash: str
