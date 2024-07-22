import pytest
from src.users import UserDB
from src.models import User
from src.exceptions import UserNotFoundException


@pytest.fixture
def user_db():
    return UserDB()


def test_get_user_by_username(user_db):
    user = user_db.get_user_by_username("user")
    assert isinstance(user, User)
    assert user.username == "user"
    assert user.password == "password"
    assert user.paid is False


def test_get_user_by_username_paid_user(user_db):
    user = user_db.get_user_by_username("paid_user")
    assert isinstance(user, User)
    assert user.username == "paid_user"
    assert user.password == "password"
    assert user.paid is True


def test_get_user_by_username_not_found(user_db):
    with pytest.raises(UserNotFoundException):
        user_db.get_user_by_username("non_existent_user")
