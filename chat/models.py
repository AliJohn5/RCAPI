from django.db import models
from users.models import RCUser
# Create your models here.



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