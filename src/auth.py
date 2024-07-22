from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from .models import TokenData, User
from .config import SECRET_KEY, ALGORITHM
from .exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
)
from .users import UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_db = UserDB()


class AuthHandler:
    def __init__(self):
        self.default_expiry = timedelta(minutes=15)
        self.key = SECRET_KEY
        self.algorithm = ALGORITHM

    def create_access_token(self, data: dict, expires: timedelta) -> str:
        """
        Create an access token with the given data and expiry time.
        """
        to_encode = data.copy()
        expiry = datetime.now(UTC) + (expires or self.default_expiry)
        to_encode.update({"exp": expiry})
        encoded_jwt = jwt.encode(to_encode, self.key, self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """
        Verify the given token and return the data.
        """
        try:
            payload = jwt.decode(token, self.key, algorithms=[self.algorithm])
            username = payload.get("sub")
            if username is None:
                raise InvalidTokenException
            token_data = TokenData(username=username)
        except JWTError as exc:
            raise InvalidCredentialsException from exc
        return token_data


auth_handler = AuthHandler()


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the given token.
    """
    token_data = auth_handler.verify_token(token)
    user = user_db.get_user_by_username(token_data.username)
    if not user:
        raise UserNotFoundException
    return user
