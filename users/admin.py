from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import RCUser, Permission,Code


admin.site.register(RCUser)
admin.site.register(Permission)
admin.site.register(Code)

