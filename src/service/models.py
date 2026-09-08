from django.db import models


class UnitOfChange(models.Model):
    name = models.CharField(max_length=30)


class Service(models.Model):
    name = models.CharField(max_length=30)
    unit_of_change = models.ForeignKey(UnitOfChange, on_delete=models.CASCADE)
    show_in_meters = models.BooleanField()

    def __str__(self):
        return self.name

    @property
    def unit(self):
        return self.unit_of_change.name


class Tariff(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class ServicePrice(models.Model):
    price = models.FloatField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)


class Account(models.Model):
    TYPE_CHOICES = (("income", "Прихід"), ("expenses", "Розхід"))
    name = models.CharField(max_length=30)
    type = models.CharField(choices=TYPE_CHOICES, default="income", max_length=15)
