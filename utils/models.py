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



class Post(models.Model):
    author = models.ForeignKey(RCUser,on_delete=models.PROTECT,related_name="MyPosts",null=True,blank=True,db_constraint=False)
    content = models.TextField(blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_for_web_and_app = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self) -> str:
        return  f"{self.author.email}: {self.content[0:20]}"


class PostImage(models.Model):
    image = models.ImageField(upload_to="photos/%y/%m/%d/",blank=True,null=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="MyImages")
    signed_url = models.TextField(blank=True, null=True)
    signed_url_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return  f"{self.post.author.email}: {self.post.content[0:20]}"