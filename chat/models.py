from django.db import models
from users.models import RCUser
# Create your models here.

import string
import random
from django.db import models

def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class MyGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(RCUser, related_name='mygroups', blank=True)

    def __str__(self) -> str:
        return self.name

class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(RCUser, on_delete=models.DO_NOTHING, blank=True, null=True,db_constraint=False)
    group = models.ManyToManyField(MyGroup, blank=True, related_name="mymessages")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.content
    class Meta:
        ordering = ['-date']




def generate_random_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class GroupCode(models.Model):
    code = models.CharField(max_length=15, blank=True, editable=False)
    group_name = models.CharField(max_length=50,)
    date = models.DateTimeField(auto_now_add=True,editable=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_random_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.group_name