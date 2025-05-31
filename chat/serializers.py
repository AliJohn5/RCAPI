from .models import *
from rest_framework.serializers import ModelSerializer
from users.serializers import RCUserSerializer





class MyGroupSerializer(ModelSerializer):
    members = RCUserSerializer(many=True,read_only = True)
    class Meta:
        model = MyGroup
        fields = ('pk','name','members')


class MessageSerializer(ModelSerializer):
    author = RCUserSerializer(many=False,read_only = True)
    group = MyGroupSerializer(many=True,read_only = True)
    class Meta:
        model = Message
        fields = ('pk','content','author','group','date')
