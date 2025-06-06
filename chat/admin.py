from django.contrib import admin
from .models import MyGroup,Message,GroupCode
# Register your models here.
admin.site.register(MyGroup)
admin.site.register(Message)
admin.site.register(GroupCode)
