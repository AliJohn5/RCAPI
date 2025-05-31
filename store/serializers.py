from .models import *
from rest_framework import serializers
from users.serializers import RCUserSerializer

class ClosetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Closet
        fields = "__all__"


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    workers = RCUserSerializer(many=True,read_only = True)
    class Meta:
        model = Project
        fields = ('pk','name','workers','completion_rate','number_of_some_things','image')


class SomeThingSerializer(serializers.ModelSerializer):
    closet = ClosetSerializer(many=False, read_only=True)
    mytype = TypeSerializer(many=False, read_only=True)
    project = ProjectSerializer(many=False, read_only=True)


    class Meta:
        model = SomeThing
        fields = ('pk','name','closet','isActive','mytype','project','isPrivate','borrowed','image')


class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        print(request)
        if request:
            if obj.image:
                return request.build_absolute_uri(obj.image.url)
            return "No image available"
        return "Request object not found"
    



class SomeThingImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = SomeThing
        fields = ['id', 'name', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        print(request)
        if request:
            if obj.image:
                return request.build_absolute_uri(obj.image.url)
            return "No image available"
        return "Request object not found"