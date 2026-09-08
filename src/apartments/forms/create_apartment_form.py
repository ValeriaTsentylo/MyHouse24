# from django import forms
# from src.houses.models import Section, Floor, Tariff, House
# from src.apartments.models import Apartment
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
#
# class CreateApartmentForm(forms.ModelForm):
#     number = forms.CharField(
#         required=True,
#         label="Номер квартири",
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#     )
#     apartment_area = forms.FloatField(
#         required=True,
#         label="Площа квартири",
#         widget=forms.TextInput(attrs={"class": "form-control"}),
#     )
#     house = forms.ModelChoiceField(
#         queryset=House.objects.all(),
#         required=True,
#         label="Дім",
#         widget=forms.Select(attrs={"class": "form-control select2"}),
#     )
#     section = forms.ModelChoiceField(
#         queryset=Section.objects.none(),  # Порожнє значення, поки дім не вибрано
#         required=True,
#         label="Секція",
#         widget=forms.Select(attrs={"class": "form-control select2"}),
#     )
#     floor = forms.ModelChoiceField(
#         queryset=Floor.objects.none(),  # Порожнє значення, поки дім не вибрано
#         required=True,
#         label="Поверх",
#         widget=forms.Select(attrs={"class": "form-control select2"}),
#     )
#     owner = forms.ModelChoiceField(
#         queryset=User.objects.filter(is_staff=False),
#         required=False,
#         label="Власник",
#         widget=forms.Select(attrs={"class": "form-control select2"}),
#     )
#     tariff = forms.ModelChoiceField(
#         queryset=Tariff.objects.all(),
#         required=False,
#         label="Тариф",
#         widget=forms.Select(attrs={"class": "form-control select2"}),
#     )
#
#     class Meta:
#         model = Apartment
#         fields = [
#             "number",
#             "apartment_area",
#             "house",
#             "section",
#             "floor",
#             "owner",
#             "tariff",
#         ]


from django import forms
from django.contrib.auth import get_user_model

from src.apartments.models import Apartment
from src.houses.models import Floor, House, Section
from src.service.models import Tariff

User = get_user_model()


class CreateApartmentForm(forms.ModelForm):
    number = forms.CharField(
        required=True,
        label="Номер квартири",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    apartment_area = forms.FloatField(
        required=True,
        label="Площа квартири",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    house = forms.ModelChoiceField(
        queryset=House.objects.all(),
        required=True,
        label="Дім",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),  # Порожнє значення, поки дім не вибрано
        required=True,
        label="Секція",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    floor = forms.ModelChoiceField(
        queryset=Floor.objects.none(),  # Порожнє значення, поки дім не вибрано
        required=True,
        label="Поверх",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    owner = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False),
        required=False,
        label="Власник",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(),
        required=False,
        label="Тариф",
        widget=forms.Select(attrs={"class": "form-control select2"}),
    )

    class Meta:
        model = Apartment
        fields = [
            "number",
            "apartment_area",
            "house",
            "section",
            "floor",
            "owner",
            "tariff",
        ]

    # Оновлення queryset для полів section і floor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        house_id = self.initial.get("house") or self.data.get("house")
        if house_id:
            self.fields["section"].queryset = Section.objects.filter(house_id=house_id)
            self.fields["floor"].queryset = Floor.objects.filter(house_id=house_id)

    # Валідація поля section
    def clean_section(self):
        section = self.cleaned_data.get("section")
        house = self.cleaned_data.get("house")
        if section and not Section.objects.filter(id=section.id, house=house).exists():
            raise forms.ValidationError("Обрана секція не відповідає вибраному будинку.")
        return section

    # Валідація поля floor
    def clean_floor(self):
        floor = self.cleaned_data.get("floor")
        house = self.cleaned_data.get("house")
        if floor and not Floor.objects.filter(id=floor.id, house=house).exists():
            raise forms.ValidationError("Обраний поверх не відповідає вибраному будинку.")
        return floor
