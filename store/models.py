from django.db import models
from users.models import RCUser

class Closet(models.Model):
    name = models.CharField(max_length=100)
    number_of_some_things = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.name
    
class Type(models.Model):
    name = models.CharField(max_length=100)
    number_of_some_things = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)
    workers = models.ManyToManyField(RCUser,blank=True,related_name = "projects")
    completion_rate = models.IntegerField(default=0)
    number_of_some_things = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.name


class SomeThing(models.Model):
    name = models.CharField(max_length=100)
    closet = models.ForeignKey(Closet,blank=True, null=True, on_delete=models.SET_NULL,related_name = "closet_somethings")
    isActive = models.BooleanField(default=True)
    mytype = models.ForeignKey(Type,blank=True, null=True, on_delete=models.SET_NULL,related_name = "mytype_somethings")
    project = models.ForeignKey(Project,blank=True, null=True, on_delete=models.SET_NULL,related_name = "project_somethings")
    isPrivate = models.BooleanField(default=False)
    borrowed =  models.BooleanField(default=False)
    def __str__(self) -> str:
        return self.name



class ClosetImage(models.Model):
    image = models.ImageField(upload_to="photos/%y/%m/%d/",blank=True,null=True)
    closet = models.ForeignKey(Closet,on_delete=models.CASCADE,related_name="MyImages")
    signed_url = models.TextField(blank=True, null=True)
    signed_url_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return  f"image for closet: {self.closet.name}"


class ProjectImage(models.Model):
    image = models.ImageField(upload_to="photos/%y/%m/%d/",blank=True,null=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="MyImages")
    signed_url = models.TextField(blank=True, null=True)
    signed_url_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return  f"image for project: {self.project.name}"


class SomeThingImage(models.Model):
    image = models.ImageField(upload_to="photos/%y/%m/%d/",blank=True,null=True)
    someThing = models.ForeignKey(SomeThing,on_delete=models.CASCADE,related_name="MyImages")
    signed_url = models.TextField(blank=True, null=True)
    signed_url_generated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return  f"image for something: {self.project.name}"