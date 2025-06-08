from django.contrib import admin
from .models import MyGroup,Message,GroupCode
# Register your models here.
from unfold.admin import ModelAdmin


@admin.register(MyGroup)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(GroupCode)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(Message)
class CustomAdminClass(ModelAdmin):
    pass

#admin.site.register(MyGroup)
#admin.site.register(Message)
#admin.site.register(GroupCode)
