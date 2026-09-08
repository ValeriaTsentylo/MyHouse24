from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from src.core.models import GalleryImage
from src.roles.models import RolePermission


class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ("new", "Новий"),
        ("active", "Активний"),
        ("disabled", "Неактивний"),
    )

    name = models.CharField(max_length=50, blank=True)
    birthday_date = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    viber = models.CharField(max_length=20, null=True, blank=True, unique=True)
    telegram = models.CharField(max_length=20, null=True, blank=True, unique=True)
    user_avatar = models.OneToOneField(
        GalleryImage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_avatar",
    )
    about_me = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    role = models.ForeignKey(
        RolePermission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users_with_role",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        permissions = [
            ("view_dashboard", "Can view dashboard"),
            ("view_payment_section", "Can view payment section"),
            ("view_personal_account", "Can view personal account"),
            ("view_apartments", "Can view apartments"),
            ("view_apartments_owners", "Can view apartments owners"),
            ("view_houses", "Can view houses"),
            ("view_messages", "Can view messages"),
            ("view_master_application", "Can view master application"),
            ("view_services_house", "Can view services house"),
            ("view_manage_site", "Can manage site"),
            ("view_system_settings", "Can view system settings"),
            ("view_services", "Can view services"),
            ("view_tariffs", "Can view tariffs"),
            ("view_roles", "Can view roles"),
            ("view_users", "Can view users"),
            ("view_payment_details", "Can view payment details"),
            ("payment_section", "Can access payment section"),
            ("master_application", "Can access master application"),
            ("services_house", "Can access services house"),
        ]

    def __str__(self):
        return self.name if self.name else self.email

    def has_permission(self, perm_codename):
        """
        Check if user has a specific permission
        """
        if self.is_superuser:
            return True
        if not self.role_id:
            return False
        return self.role.permissions.filter(codename=perm_codename).exists()

    def has_role(self, role_name):
        return self.role and self.role.name == role_name
