from .models import *
from rest_framework.serializers import ModelSerializer, SerializerMethodField,CharField
from users.serializers import RCUserSerializer
from store.serializers import SomeThingSerializer
from users.utils import get_b2_signed_url

from datetime import timedelta
from django.utils import timezone


class BorrowSerializer(ModelSerializer):
    person = RCUserSerializer(many=True,read_only = True)
    something = SomeThingSerializer(many=False,read_only = True)

    class Meta:
        model = Borrow
        fields = ('pk','person','something','date_start','date_end','is_returned')



class PostImageSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = PostImage
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
    
class PostSerializer(ModelSerializer):
    MyImages = PostImageSerializer(many=True, read_only=True)
    author = RCUserSerializer(read_only=True)


    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'date', 'MyImages','is_for_web_and_app']
        read_only_fields = ['author']