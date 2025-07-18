from users.utils import get_b2_signed_url
from .models import *
from rest_framework.serializers import ModelSerializer,Serializer,CharField,SerializerMethodField
from users.serializers import RCUserSerializer
from datetime import timedelta
from django.utils import timezone



class MyGroupSerializer(ModelSerializer):
    members = RCUserSerializer(many=True,read_only = True)
    class Meta:
        model = MyGroup
        fields = ('pk','name','members')

class MessageFileSerializer(ModelSerializer):
    file = SerializerMethodField()

    class Meta:
        model = MessageFile
        fields = ['id', 'file','origin_name']

    def get_file(self, obj):
        now = timezone.now()
        if obj.signed_url and obj.signed_url_generated_at:
            if now - obj.signed_url_generated_at < timedelta(days=5):
                return obj.signed_url 

        
        new_signed_url = get_b2_signed_url(obj.name)
        obj.signed_url = new_signed_url
        obj.signed_url_generated_at = now
        obj.save(update_fields=["signed_url", "signed_url_generated_at"])

        return new_signed_url
    
class MessageSerializer(ModelSerializer):
    author = RCUserSerializer(many=False,read_only = True)
    group = MyGroupSerializer(many=True,read_only = True)
    file = SerializerMethodField()
    class Meta:
        model = Message
        fields = ('pk','content','author','group','date','is_contain_file','file')
    
    def get_file(self,obj):
        messages = MessageFile.objects.filter(
            message = obj
        )
        if not messages.exists():
            return {
                'file_name': "",
                'file_url': "",
                'origin_name': ""
            }
        
        file = messages.first()
        now = timezone.now()
        if file.signed_url and file.signed_url_generated_at:
            if now - file.signed_url_generated_at < timedelta(days=5):
                return {
                'file_name':file.name,
                'file_url': file.signed_url,
                'origin_name': file.origin_name
            }

        
        new_signed_url = get_b2_signed_url(file.name)
        file.signed_url = new_signed_url
        file.signed_url_generated_at = now
        file.save(update_fields=["signed_url", "signed_url_generated_at"])

        return {
                'file_name':file.name,
                'file_url': file.signed_url,
                'origin_name': file.origin_name
            }



class GroupCodeSerializer(ModelSerializer):
    class Meta:
        model = GroupCode
        fields = [ 'group_name', 'code' , 'date']
        read_only_fields = ['code'] 



