from django.contrib import admin
from .models import *
# Register your models here.
#admin.site.register(Borrow)

from unfold.admin import ModelAdmin


@admin.register(Borrow)
class CustomAdminClass(ModelAdmin):
    pass