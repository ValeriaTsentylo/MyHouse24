from django import forms
from django.forms import inlineformset_factory

from src.houses.models import Floor, House


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ["id", "number"]
        labels = {"number": "Номер"}
        widgets = {
            "number": forms.TextInput(attrs={"class": "form-control"}),
        }


FloorFormSet = inlineformset_factory(House, Floor, form=FloorForm, extra=0, can_delete=True)
