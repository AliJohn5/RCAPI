from datetime import timedelta
from django.utils import timezone
from users.utils import get_b2_signed_url
from .models import *
from rest_framework import serializers
from users.serializers import RCUserSerializer
from utils.models import Borrow
from django.db.models import Q



class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image']

    def get_image(self, obj):
        now = timezone.now()
        if obj.signed_url and obj.signed_url_generated_at:
            if now - obj.signed_url_generated_at < timedelta(days=5):
                return obj.signed_url 

        
        new_signed_url = get_b2_signed_url(obj.image.name)
        obj.signed_url = new_signed_url
        obj.signed_url_generated_at = now
        obj.save(update_fields=["signed_url", "signed_url_generated_at"])

        return new_signed_url



class SomeThingImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SomeThingImage
        fields = ['id', 'image']

    def get_image(self, obj):
        
        now = timezone.now()
        if obj.signed_url and obj.signed_url_generated_at:
            if now - obj.signed_url_generated_at < timedelta(days=5):
                return obj.signed_url 

        
        new_signed_url = get_b2_signed_url(obj.image.name)
        obj.signed_url = new_signed_url
        obj.signed_url_generated_at = now
        obj.save(update_fields=["signed_url", "signed_url_generated_at"])

        return new_signed_url
    


class ClosetSerializer(serializers.ModelSerializer):
    numberOfMaterials = serializers.SerializerMethodField()

    class Meta:
        model = Closet
        fields = ['pk', 'name', 'description','numberOfMaterials']
    
    def get_numberOfMaterials(self,obj):
        return SomeThing.objects.filter(Q(closet = obj)).count()


class TypeSerializer(serializers.ModelSerializer):
    numberOfMaterials = serializers.SerializerMethodField()

    class Meta:
        model = Type
        fields = ['pk', 'name', 'description','numberOfMaterials']
    
    def get_numberOfMaterials(self,obj):
        return SomeThing.objects.filter(Q(mytype = obj)).count()

class ProjectSerializer(serializers.ModelSerializer):
    workers = serializers.SerializerMethodField()
    MyImages = ProjectImageSerializer(many=True, read_only=True)
    numberOfSomeThings = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('pk','name','workers','completion_rate','numberOfSomeThings','MyImages')
    
    def get_numberOfSomeThings(self,obj):
        return SomeThing.objects.filter(Q(project=obj)).count()
    
    def get_workers(self,obj):
        users = obj.workers.all()
        ans = []
        for user in users:
            ans.append(user.email)
        return ans


class SomeThingSerializer(serializers.ModelSerializer):
    closet = ClosetSerializer(many=False, read_only=True)
    mytype = TypeSerializer(many=False, read_only=True)
    project = ProjectSerializer(many=False, read_only=True)
    MyImages = SomeThingImageSerializer(many=True, read_only=True)
    borrowedBy = serializers.SerializerMethodField()
    borrowed = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()





    class Meta:
        model = SomeThing
        fields = ('pk','name','closet','isActive','mytype','project','isPrivate','borrowed', 'MyImages','borrowedBy','status')
    
    def get_borrowedBy(self,obj):
        borrow = Borrow.objects.filter(Q(something = obj))


        if(not borrow):
            return ""
        
        if(not borrow[0].is_accepted):
            return ""
        
        ans = borrow[0].person.email
        return ans
    
    def get_borrowed(self,obj):
        borrow = Borrow.objects.filter(Q(something = obj))


        if(not borrow):
            return False
        
        if(not borrow[0].is_accepted):
            return False
        
     
        return True
    
    def get_status(seld,obj):

        try:
            b = Borrow.objects.get(something = obj)
            if(b.is_accepted):
                return "borrowed"
            else:
                return "pending"
        except:
            return "available"
        


    


