import io
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
from .models import MyGroup, Message,MessageFile
from .serializers import MessageSerializer
from users.models import RCUser
from rest_framework.authtoken.models import Token
import base64
import os
from django.conf import settings
from django.core.files.base import ContentFile
import os
import random
import string
import tempfile
from django.conf import settings
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime, timedelta, timezone
from django.utils import timezone as dt

@sync_to_async
def generate_random_string_file(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@sync_to_async
def upload_file_to_backblaze(file, existing_image=None, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
    if existing_image:
        existing_image.delete()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    # Setup B2 API
    app_id = settings.AWS_ACCESS_KEY_ID
    app_key = settings.AWS_SECRET_ACCESS_KEY
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account('production', app_id, app_key)

    bucket = b2_api.get_bucket_by_name(bucket_name)

    
    now = datetime.now(timezone.utc)
    folder_path = now.strftime("files/%Y/%m/%d")
    random_filename = generate_random_string_file(15)
    full_file_name = f"{folder_path}/{random_filename}"

    uploaded_file = bucket.upload_local_file(
        local_file=temp_file_path,
        file_name=full_file_name,
        content_type='auto'
    )

    os.remove(temp_file_path)

    # 🔐 Generate signed URL valid for 30 days
    auth_token = bucket.get_download_authorization(
        file_name_prefix=full_file_name,
        valid_duration_in_seconds=24 * 60 * 60 * 6 
    )
    base_url = b2_api.get_download_url_for_file_name(bucket_name, full_file_name)
    signed_url = f"{base_url}?Authorization={auth_token}"

    return {
        "file_name": full_file_name,  # includes folders
        "signed_url": signed_url
    }



class ChatConsumer(AsyncWebsocketConsumer):

    # ========== Database Helpers ==========

    @sync_to_async
    def get_user_from_jwt(self, token):
        access_token = get_object_or_404(Token,key=token)
        user_id = access_token.user_id
        return RCUser.objects.get(id=user_id)

    @sync_to_async
    def get_group(self, name):
        return MyGroup.objects.get(name=name)

    @sync_to_async
    def is_member(self, user, group) -> bool:
        return group.members.filter(email=user.email).exists()

    @sync_to_async
    def create_message(self, content, author, group,file_name,file_url,origin_name):
        is_contain_file = False
        if(file_name and file_url):
            is_contain_file = True
        data = {'content': content,'is_contain_file':is_contain_file}
        serializer = MessageSerializer(data=data)
       
        
        if serializer.is_valid():
            serializer.save(author=author)
            message = Message.objects.get(pk=serializer.data['pk'])
            message.group.add(group)
            if(file_name and file_url):
                MessageFile.objects.create(
                    name = file_name,
                    origin_name=origin_name,
                    message = message,
                    signed_url_generated_at = dt.now(),
                    signed_url = file_url
                )
            return message.date, message.pk,message.is_contain_file
        
        return None,None,None

    # ========== WebSocket Lifecycle ==========

    async def connect(self):
        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = f"chat_{self.room_name}"

            # Extract Authorization header (JWT)
            headers = dict((k.lower(), v) for k, v in self.scope["headers"])
            raw_token = headers.get(b"authorization", None)
            if not raw_token:
                return await self.close()

            token_str = raw_token.decode().split(" ")[1]  # Remove "Bearer"
            self.user = await self.get_user_from_jwt(token_str)
            self.group = await self.get_group(self.room_name)

            if not await self.is_member(self.user, self.group):
                return await self.close()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except Exception as e:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # ========== Message Handling ==========

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            message = data.get("message", "").strip()
            file_base64 = data.get("fileBase64")
            file_name = data.get("fileName")
            localIndex = data.get("localIndex")

            origin_name = file_name

            if not message and not file_name:
                return  # Ignore empty messages
            
            file_url = None
           

            if file_base64 and file_name:
                file_bytes = base64.b64decode(file_base64)
                file_io = io.BytesIO(file_bytes)
    
                file = InMemoryUploadedFile(
                    file_io,
                    field_name='file',
                    name=file_name,
                    content_type='application/octet-stream',
                    size=len(file_bytes),
                    charset=None
                )
    
                result = await upload_file_to_backblaze(file)
                #result = {"signed_url":"ali"}
                file_url = result["signed_url"]
                file_name = result['file_name']
            
            
            
            
            # Create message in DB (only sender)
            date , pk, is_contain_file = await self.create_message(message, self.user, self.group,file_name,file_url,origin_name)
            
            if not date:
                return
            name = ""

            if(self.user.first_name):
                name = self.user.first_name
                if(self.user.last_name):
                    name = name +" "+ self.user.last_name
            elif(self.user.last_name):
                name = self.user.last_name
            # Broadcast to group

            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "name": name,
                    "email": self.user.email,
                    "date": str(date),
                    "groupeName": self.room_name,
                    'pk': pk,
                    "is_contain_file":is_contain_file,
                    "file_url":file_url,
                    "origin_name":origin_name,
                    'localIndex':localIndex
                }
            )
        except Exception as e:
            print("Error" , e)
            pass  # You can log error here

    async def chat_message(self, event):
        file_url = ""
        origin_name = ""
        localIndex = -1

        if(event["file_url"]):
            file_url =event["file_url"]

        if(event["origin_name"]):
            origin_name =event["origin_name"]
        
        if(event["localIndex"] != None):
            localIndex =event["localIndex"]
        
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "emailFrom": event["email"],
            "nameFrom": event["name"],
            "date": event["date"],
            "groupeName": event["groupeName"],
            "is_contain_file" : event["is_contain_file"],
            "pk":event["pk"],
            "file_url":file_url,
            "origin_name":origin_name,
            "localIndex":localIndex
        }))
