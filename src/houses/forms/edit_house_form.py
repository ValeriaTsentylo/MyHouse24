from django import forms

from src.houses.models import House


class EditHouseForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        required=True,
        label="Назва",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    adress = forms.CharField(
        required=True,
        label="Адреса",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    image1 = forms.ImageField(
        required=False,
        label="Зображення #1 (522x350)",
        widget=forms.FileInput(),
    )
    image2 = forms.ImageField(
        required=False,
        label="Зображення #2 (248x160)",
        widget=forms.FileInput(),
    )
    image3 = forms.ImageField(
        required=False,
        label="Зображення #3 (248x160)",
        widget=forms.FileInput(),
    )
    image4 = forms.ImageField(
        required=False,
        label="Зображення #4 (248x160)",
        widget=forms.FileInput(),
    )
    image5 = forms.ImageField(
        required=False,
        label="Зображення #5 (248x160)",
        widget=forms.FileInput(),
    )

    class Meta:
        model = House
        fields = ["name", "adress", "image1", "image2", "image3", "image4", "image5"]
