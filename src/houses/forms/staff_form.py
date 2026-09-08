from django import forms
from django.forms import inlineformset_factory

from src.houses.models import House, Staff
from src.users.models import User


class StaffForm(forms.ModelForm):
    role = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"}),
        label="Роль",
    )

    class Meta:
        model = Staff
        fields = ["id", "user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(is_staff=True)
        self.fields["user"].widget.attrs.update({"class": "form-control select2"})

        if self.instance and self.instance.user and self.instance.user.role:
            self.fields["role"].initial = self.instance.user.role.get_display_name()

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        if user:
            cleaned_data["role"] = user.role
        return cleaned_data


StaffFormSet = inlineformset_factory(House, Staff, form=StaffForm, extra=0, can_delete=True)
#
# from django import forms
# from django.forms import inlineformset_factory
# from django_select2.forms import ModelSelect2Widget
# from src.houses.models import Staff, House
# from src.users.models import User
#
#
# class StaffForm(forms.ModelForm):
#     role = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={"readonly": "readonly", "class": "form-control"}),
#         label="Роль",
#     )
#
#     class Meta:
#         model = Staff
#         fields = ["id", "user"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["user"].queryset = User.objects.filter(is_staff=True)  # Тільки staff користувачі
#         self.fields["user"].widget = ModelSelect2Widget(
#             model=User,
#             search_fields=["name__icontains"],  # Пошук по імені користувача
#             queryset=User.objects.filter(is_staff=True),  # Тільки staff користувачі
#             attrs={"class": "form-control select2", "data-placeholder": "Оберіть користувача"},
#         )
#
#     def clean(self):
#         cleaned_data = super().clean()
#         user = cleaned_data.get("user")
#         if user:
#             cleaned_data["role"] = user.role
#         return cleaned_data
#
# StaffFormSet = inlineformset_factory(
#     House, Staff, form=StaffForm, extra=0, can_delete=True
# )
