from django.db import models

from src.apartments.models import Apartment
from src.houses.models import House, Section
from src.service.models import Account, Service
from src.users.models import User


class Receipt(models.Model):  # квитанція
    RECEIPT_PAYMENT_STATUS_CHOICES = (
        ("paid", "оплачено"),
        ("unpaid", "не оплачено"),
        ("part paid", "оплачено частково"),
    )

    number = models.IntegerField()
    date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    pay_status = (
        models.CharField(choices=RECEIPT_PAYMENT_STATUS_CHOICES, default="unpaid", max_length=30),
    )
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    receipt_status = models.BooleanField(default=False)  # проведена
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    amount = models.FloatField()


class PersonalAccount(models.Model):
    STATUS_CHOICES = (
        ("active", "активний"),
        ("disabled", "неактивний"),
    )

    number = models.IntegerField()
    status = models.CharField(choices=STATUS_CHOICES, default="new", max_length=14)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)


class InStatement(models.Model):  # прихідна відомість
    number = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_instatements")
    personal_account = models.ForeignKey(PersonalAccount, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.FloatField()
    comments = models.TextField()
    status = models.BooleanField(default=False)


class ExStatement(models.Model):  # розхідна відомість
    number = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField()
    status = models.BooleanField(default=False)
