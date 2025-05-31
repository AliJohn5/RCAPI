
from rest_framework import serializers
from .models import RCUser, Permission,Code
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

us = get_user_model()

class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)
            
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RCUserSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)
    
    class Meta:
        model = RCUser
        fields = ('email', 'first_name', 'last_name','phone_number', 'password', 'permissions','image')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        
        user = RCUser(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

    

class CodeSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = '__all__'




class RCuserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RCUser
        fields = ['image']