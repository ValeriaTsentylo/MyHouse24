import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


def _make_user(email, **extra):
    user = User(email=email, about_me="", **extra)
    user.set_password("pass12345")
    user.save()
    return user


@pytest.fixture
def resident(db):
    return _make_user("resident@example.com", name="Resident")


@pytest.fixture
def staff_user(db):
    return _make_user("staff@example.com", name="Staff", is_staff=True)


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user)
    return client
