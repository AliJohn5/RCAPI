from .models import *
from rest_framework.serializers import ModelSerializer
from users.serializers import RCUserSerializer
from store.serializers import SomeThingSerializer

class BorrowSerializer(ModelSerializer):
    person = RCUserSerializer(many=True,read_only = True)
    something = SomeThingSerializer(many=False,read_only = True)

    class Meta:
        model = Borrow
        fields = ('pk','person','something','date_start','date_end','is_returned')