from django.db import models
from users.models import RCUser
from store.models import SomeThing

class Borrow(models.Model):
    person = models.ManyToManyField(RCUser,related_name="borrowed_by_user",db_constraint=False)
    something = models.ForeignKey(SomeThing,on_delete=models.PROTECT,related_name="borrow_something",null=True,blank=True,db_constraint=False)
    date_start = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(null=True,blank=True)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return  self.something.name


