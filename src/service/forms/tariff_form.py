from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import Select

from src.service.models import Service, ServicePrice, Tariff


class ServiceSelectWidget(Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:  # Додаємо data-unit тільки для валідних значень
            try:
                # Передбачається, що `Service` — це модель
                service = Service.objects.get(pk=value)
                option["attrs"]["data-unit"] = service.unit_of_change.name
            except Service.DoesNotExist:
                pass
        return option


class TariffForm(forms.ModelForm):
    name = forms.CharField(
        max_length=30,
        required=True,
        label="Назва тарифу",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    description = forms.CharField(
        required=True,
        label="Опис тарифу",
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Tariff
        fields = [
            "id",
            "name",
            "description",
        ]


class ServicePriceForm(forms.ModelForm):
    class Meta:
        model = ServicePrice
        fields = ["id", "service", "price"]
        widgets = {
            "service": ServiceSelectWidget(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "service" in self.fields:
            # Оновлення вибору (choices) і додавання data-unit
            self.fields["service"].widget.choices = [
                (service.id, service.name) for service in self.fields["service"].queryset
            ]


ServicePriceFormSet = inlineformset_factory(
    parent_model=Tariff,
    model=ServicePrice,
    form=ServicePriceForm,
    extra=0,
    can_delete=True,
)
