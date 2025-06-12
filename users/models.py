from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Permission(models.Model):
    permission = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.permission

class RCUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class RCUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField(Permission, related_name='users', blank=True)
    image = models.ImageField(upload_to="photos/%y/%m/%d/",blank=True,null=True)
    signed_url = models.TextField(blank=True, null=True)
    signed_url_generated_at = models.DateTimeField(blank=True, null=True)
    objects = RCUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    


class Code(models.Model):
    code = models.CharField(max_length=10)
    user = models.ForeignKey(RCUser,on_delete=models.PROTECT,related_name="codes",db_constraint=False)

    def __str__(self):
        return self.user.email



class PermissionRequest(models.Model):
    permission = models.CharField(max_length=255)
    user = models.ForeignKey(RCUser,on_delete=models.CASCADE,related_name="requests_to_upgrade")
    def __str__(self) -> str:
        return self.permission