from django.db import models
from django.utils import timezone, formats
from django.template.defaultfilters import date


class Bills(models.Model):  # Список платежей
    bill = models.CharField(max_length=32)

    def __str__(self):
        return self.bill


class FuelTypes(models.Model):  # Виды топлива
    id = models.SmallIntegerField(primary_key=True)
    type = models.CharField(max_length=4)

    def __str__(self):
        return self.type


class Railcars(models.Model):  # Вагоны
    railcar = models.CharField(max_length=8)
    bill = models.ForeignKey(Bills, on_delete=models.PROTECT)
    fuel = models.ForeignKey(FuelTypes, on_delete=models.PROTECT)
    fuel_brand = models.CharField(max_length=32)
    volume = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return str(self.railcar)


class Tracking(models.Model):  # Отслеживание вагонов
    time = models.DateTimeField(default=timezone.now)
    railcar = models.ForeignKey(Railcars, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    comment = models.TextField(max_length=200, blank=True, default='')

    def __str__(self):
        _datetime = self.time.astimezone(timezone.get_current_timezone())
        return '{}: {}'.format(formats.date_format(_datetime, 'SHORT_DATETIME_FORMAT'),
                               self.railcar)
