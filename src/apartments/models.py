from django.db import models

from src.houses.models import Floor, House, Section
from src.service.models import Tariff
from src.users.models import User


class Apartment(models.Model):
    number = models.IntegerField()
    apartment_area = models.FloatField(default=0.0)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, blank=True)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, null=True, blank=True)


class ApartmentOwner(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": False},
        null=True,
        blank=True,
        related_name="apartments",
    )
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.name if self.user.name else self.user.email} - {self.apartment}"
