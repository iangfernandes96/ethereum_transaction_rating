import pytest
from datetime import timedelta, datetime, UTC
from jose import jwt
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.auth import AuthHandler, get_current_user
from src.models import User
from src.exceptions import InvalidCredentialsException, UserNotFoundException
from src.config import SECRET_KEY, ALGORITHM
from src.users import UserDB

from src.main import app

client = TestClient(app)


@pytest.fixture
def auth_handler():
    return AuthHandler()


@pytest.fixture
def token():
    auth_handler = AuthHandler()
    data = {"sub": "testuser"}
    return auth_handler.create_access_token(data, expires=timedelta(minutes=15))


@pytest.fixture
def expired_token():
    auth_handler = AuthHandler()
    data = {"sub": "testuser"}
    return auth_handler.create_access_token(data, expires=timedelta(seconds=-1))


def test_create_access_token(auth_handler):
    data = {"sub": "testuser"}
    token = auth_handler.create_access_token(data, expires=timedelta(minutes=15))
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "testuser"
    assert decoded_data["exp"] > datetime.timestamp(datetime.now(UTC))


def test_verify_token(auth_handler, token):
    token_data = auth_handler.verify_token(token)
    assert token_data.username == "testuser"


def test_verify_token_invalid(auth_handler):
    invalid_token = "invalid_token"
    with pytest.raises(InvalidCredentialsException):
        auth_handler.verify_token(invalid_token)


def test_verify_token_expired(auth_handler, expired_token):
    with pytest.raises(InvalidCredentialsException):
        auth_handler.verify_token(expired_token)


@patch.object(
    UserDB,
    "get_user_by_username",
    return_value=User(username="testuser", password="testpassword", paid=False),
)
def test_get_current_user(mock_get_user_by_username, token):
    user = get_current_user(token=token)
    assert user.username == "testuser"


@patch.object(UserDB, "get_user_by_username", return_value=None)
def test_get_current_user_not_found(mock_get_user_by_username, token):
    with pytest.raises(UserNotFoundException):
        get_current_user(token=token)
