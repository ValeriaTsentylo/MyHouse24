from django import forms
from django.core.exceptions import ValidationError

from src.roles.models import RolePermission
from src.users.models import User


class EditStaffUserForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        required=True,
        label="ПІБ",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone = forms.CharField(
        required=True,
        label="Телефон",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    role = forms.ModelChoiceField(
        queryset=RolePermission.objects.all(),
        required=True,
        label="Роль",
        empty_label="Оберіть роль",
        widget=forms.Select(attrs={"class": "form-control select2bs4", "style": "width: 100%;"}),
    )
    status = forms.ChoiceField(
        choices=User.STATUS_CHOICES,
        required=True,
        label="Статус",
        widget=forms.Select(attrs={"class": "form-control select2bs4", "style": "width: 100%;"}),
    )
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "id": "password1"}),
        label="Пароль",
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "id": "password2"}),
        label="Повторити пароль",
    )

    class Meta:
        model = User
        fields = ["name", "email", "phone", "role", "status"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Паролі не співпадають.")

        return password2
