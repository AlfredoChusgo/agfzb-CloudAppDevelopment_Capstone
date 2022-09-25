from django.contrib import admin
from .models import CarModel, CarMake


# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel

# CarModelAdmin class
class CardModelAdmin(admin.ModelAdmin):
    pass

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
# Register models here
admin.site.register(CarModel,CardModelAdmin)
admin.site.register(CarMake,CarMakeAdmin)