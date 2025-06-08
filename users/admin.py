from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import RCUser, Permission,Code,PermissionRequest
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm



class CustomUserAdmin(BaseUserAdmin, ModelAdmin,ImportExportModelAdmin):  # Inherits properly
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('first_name', 'is_staff', 'is_active')
    filter_horizontal = ('groups', 'permissions')
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'is_active', 'is_staff')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

admin.site.unregister(Group)

# Correctly register it:
admin.site.register(RCUser, CustomUserAdmin)


@admin.register(Permission)
class CustomAdminClass(ModelAdmin):
    pass

@admin.register(Code)
class CustomAdminClass(ModelAdmin):
    pass
@admin.register(PermissionRequest)
class CustomAdminClass(ModelAdmin):
    pass

#admin.site.register(RCUser)
#admin.site.register(Permission)
#admin.site.register(Code)
#admin.site.register(PermissionRequest)

