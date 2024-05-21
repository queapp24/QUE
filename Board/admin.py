from django.contrib import admin
from .models import Rotation, Driver, Arrival, Departure, Hidden

admin.site.register(Rotation)
admin.site.register(Driver)
admin.site.register(Arrival)
admin.site.register(Departure)
admin.site.register(Hidden)