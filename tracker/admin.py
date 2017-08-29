from django.contrib import admin

from .models import Bills, Tracking, Railcars, FuelTypes

# Register your models here.

admin.site.register(Bills)
admin.site.register(Tracking)
admin.site.register(Railcars)
admin.site.register(FuelTypes)