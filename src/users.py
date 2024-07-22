from .models import User
from .exceptions import UserNotFoundException


class UserDB:
    users = {}
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.users = {
            "user": {
                "username": "user",
                "password": "password",
                "paid": False,
            },
            "paid_user": {
                "username": "paid_user",
                "password": "password",
                "paid": True,
            },
        }

    def get_user_by_username(self, username: str) -> User:
        """
        Get a user by their username."""
        user = self.users.get(username)
        if user:
            return User(**user)
        raise UserNotFoundException
