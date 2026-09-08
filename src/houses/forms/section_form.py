from django import forms
from django.forms import inlineformset_factory

from src.houses.models import House, Section


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["id", "name"]
        labels = {"name": "Назва"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


SectionFormSet = inlineformset_factory(House, Section, form=SectionForm, extra=0, can_delete=True)
