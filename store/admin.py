from django.contrib import admin
from .models import *
# Register your models here.

from unfold.admin import ModelAdmin


@admin.register(Closet)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(Type)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(Project)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(SomeThing)
class CustomAdminClass(ModelAdmin):
    pass

#admin.site.register(Closet)
#admin.site.register(Type)
#admin.site.register(Project)
#admin.site.register(SomeThing)
