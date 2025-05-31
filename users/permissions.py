from rest_framework import permissions
from .models import Permission



class MyHasPermission(permissions.BasePermission):
    
    def __init__(self,param):
        self.permission_name = param

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.permissions.filter(permission=self.permission_name).exists()
        return False
    

def HasPermission(permission_name):
    class HasPermissionFactory(MyHasPermission):
        def __init__(self):
            super().__init__(permission_name)
    
    return HasPermissionFactory
