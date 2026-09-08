from django import forms
from django.forms import modelformset_factory

from src.service.models import Service, UnitOfChange


class UnitForm(forms.ModelForm):
    name = forms.CharField(
        max_length=30,
        required=True,
        label="Одиниця виміру",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = UnitOfChange
        fields = [
            "id",
            "name",
        ]


class ServiceForm(forms.ModelForm):
    name = forms.CharField(
        max_length=30,
        required=True,
        label="Назва послуги",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    unit_of_change = forms.ModelChoiceField(
        queryset=UnitOfChange.objects.all(),
        required=True,
        label="Одиниця виміру",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    show_in_meters = forms.BooleanField(
        required=False,
        label="Показувати в лічильниках",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Service
        fields = ["id", "name", "unit_of_change", "show_in_meters"]


UnitFormSet = modelformset_factory(
    model=UnitOfChange,
    form=UnitForm,
    extra=0,
    can_delete=True,
)

ServiceFormSet = modelformset_factory(
    model=Service,
    form=ServiceForm,
    extra=0,
    can_delete=True,
)
