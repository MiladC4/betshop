from django.contrib import admin
from .models import Slip, PlacedBet


# Register your models here.
admin.site.register(Slip)
admin.site.register(PlacedBet)