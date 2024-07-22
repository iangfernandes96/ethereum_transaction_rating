from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.auth import auth_handler
from datetime import timedelta
from src.models import LoginResponse
from src.users import UserDB
from src.exceptions import InvalidCredentialsException
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, TOKEN_ENDPOINT

user_db = UserDB()
user_router = APIRouter()


@user_router.post(TOKEN_ENDPOINT, response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):  # noqa
    user = user_db.get_user_by_username(form_data.username)
    if user.password != form_data.password:
        raise InvalidCredentialsException()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user.username}
    access_token = auth_handler.create_access_token(
        data=token_data, expires=access_token_expires
    )
    return LoginResponse(access_token=access_token)
