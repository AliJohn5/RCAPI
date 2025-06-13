from datetime import timedelta, timezone

from users.utils import get_b2_signed_url
from .models import *
from rest_framework import serializers
from users.serializers import RCUserSerializer



class ClosetImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ClosetImage
        fields = ['id', 'image']

    def get_image(self, obj):
        now = timezone.now()
        if obj.signed_url and obj.signed_url_generated_at:
            if now - obj.signed_url_generated_at < timedelta(days=6):
                return obj.signed_url 

        
        new_signed_url = get_b2_signed_url(obj.image.name)
        obj.signed_url = new_signed_url
        obj.signed_url_generated_at = now
        obj.save(update_fields=["signed_url", "signed_url_generated_at"])

        return new_signed_url




class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image']

    def get_image(self, obj):
        now = timezone.now()
        if obj.signed_url and obj.signed_url_generated_at:
            if now - obj.signed_url_generated_at < timedelta(days=6):
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
            if now - obj.signed_url_generated_at < timedelta(days=6):
                return obj.signed_url 

        
        new_signed_url = get_b2_signed_url(obj.image.name)
        obj.signed_url = new_signed_url
        obj.signed_url_generated_at = now
        obj.save(update_fields=["signed_url", "signed_url_generated_at"])

        return new_signed_url
    


class ClosetSerializer(serializers.ModelSerializer):
    MyImages = ClosetImageSerializer(many=True, read_only=True)
    class Meta:
        model = Closet
        fields = ['id', 'name', 'number_of_some_things', 'MyImages']


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    workers = RCUserSerializer(many=True,read_only = True)
    MyImages = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('pk','name','workers','completion_rate','number_of_some_things','MyImages')


class SomeThingSerializer(serializers.ModelSerializer):
    closet = ClosetSerializer(many=False, read_only=True)
    mytype = TypeSerializer(many=False, read_only=True)
    project = ProjectSerializer(many=False, read_only=True)
    MyImages = SomeThingImageSerializer(many=True, read_only=True)


    class Meta:
        model = SomeThing
        fields = ('pk','name','closet','isActive','mytype','project','isPrivate','borrowed', 'MyImages')

    


