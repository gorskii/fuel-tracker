from django.db import models
from django.utils import timezone, formats
from django.contrib.auth.models import User
from django.http import request
from django.template.defaultfilters import date


def month_limit():
    """
    Вычисляет 30 дней от текущей даты, чтобы подставить в supply_date по умолчанию.
    """
    return timezone.localdate() + timezone.timedelta(days=30)


class Bills(models.Model):  # Список платежей
    bill = models.CharField(max_length=32, verbose_name="Номер платежа", unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Сумма")
    supplier = models.CharField(max_length=32, verbose_name="Поставщик")
    bill_date = models.DateField(default=timezone.localdate, verbose_name="Дата платежа")
    supply_date = models.DateField(default=month_limit, verbose_name="Дата поставки",
                                   help_text="Укажите предполагаемую дату поставки")

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    def __str__(self):
        return self.bill


class FuelTypes(models.Model):  # Виды топлива
    id = models.SmallIntegerField(primary_key=True, verbose_name='ИД')
    type = models.CharField(max_length=4, verbose_name="тип")

    class Meta:
        verbose_name = 'тип топлива'
        verbose_name_plural = 'типы топлива'

    def __str__(self):
        return self.type


class Railcars(models.Model):  # Вагоны
    railcar = models.CharField(max_length=8, verbose_name="вагон")
    bill = models.ForeignKey(Bills, on_delete=models.PROTECT, verbose_name="платеж")
    fuel = models.ForeignKey(FuelTypes, on_delete=models.PROTECT, verbose_name="тип топлива")
    volume = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="объем",
                                 help_text="Введите количество топлива в килограммах")

    class Meta:
        verbose_name = 'вагон'
        verbose_name_plural = 'вагоны'

    def __str__(self):
        return str(self.railcar)


class Tracking(models.Model):  # Отслеживание вагонов
    time = models.DateTimeField(default=timezone.now, verbose_name="время")
    railcar = models.ForeignKey(Railcars,
                                on_delete=models.PROTECT,
                                verbose_name="Вагон"
                                )
    amount = models.DecimalField(max_digits=10,
                                 decimal_places=4,
                                 verbose_name="Количество",
                                 help_text="Введите количество топлива в килограммах"
                                 )
    comment = models.TextField(max_length=200,
                               blank=True,
                               default='',
                               verbose_name="Комментарий"
                               )
    accepted_by = models.ForeignKey(User,
                                    null=True,
                                    on_delete=models.PROTECT,
                                    verbose_name="сотрудник"
                                    )

    class Meta:
        verbose_name = 'принятый вагон'
        verbose_name_plural = 'принятые вагоны'

    def __str__(self):
        _datetime = self.time.astimezone(timezone.get_current_timezone())
        return '{}: {}'.format(formats.date_format(_datetime, 'SHORT_DATETIME_FORMAT'),
                               self.railcar)
