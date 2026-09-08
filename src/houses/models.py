from django.db import models

from src.users.models import User


class House(models.Model):
    name = models.CharField(max_length=30)
    adress = models.CharField(max_length=40)
    image1 = models.ImageField(upload_to="images/", null=True, blank=True)
    image2 = models.ImageField(upload_to="images/", null=True, blank=True)
    image3 = models.ImageField(upload_to="images/", null=True, blank=True)
    image4 = models.ImageField(upload_to="images/", null=True, blank=True)
    image5 = models.ImageField(upload_to="images/", null=True, blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=20)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name


class Floor(models.Model):
    number = models.IntegerField()
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return str(self.number)


class Staff(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": True},
        null=True,
        blank=True,
    )
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="staff", null=True, blank=True
    )
