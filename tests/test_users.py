import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from src.roles.models import RolePermission

User = get_user_model()


@pytest.mark.django_db
def test_str_falls_back_to_email():
    user = User.objects.create(email="no-name@example.com", about_me="")
    assert str(user) == "no-name@example.com"

    user.name = "Валерія"
    assert str(user) == "Валерія"


@pytest.mark.django_db
def test_has_permission_without_role_does_not_raise():
    """Regression: role is nullable, so this used to blow up with AttributeError."""
    user = User.objects.create(email="roleless@example.com", about_me="")
    assert user.has_permission("view_houses") is False


@pytest.mark.django_db
def test_superuser_bypasses_role_permissions():
    user = User.objects.create(email="root@example.com", about_me="", is_superuser=True)
    assert user.has_permission("view_houses") is True


@pytest.mark.django_db
def test_role_permission_is_scoped_to_the_assigned_role():
    role = RolePermission.objects.create(name="manager")
    user = User.objects.create(email="manager@example.com", about_me="", role=role)
    assert user.has_permission("view_houses") is False


@pytest.mark.django_db
def test_email_is_unique():
    User.objects.create(email="dup@example.com", about_me="")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create(email="dup@example.com", about_me="")
