import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
from .models import MyGroup, Message
from .serializers import MessageSerializer
from users.models import RCUser
from rest_framework.authtoken.models import Token

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
    def create_message(self, content, author, group):
        data = {'content': content}
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=author)
            message = Message.objects.get(pk=serializer.data['pk'])
            message.group.add(group)
            return message.date
        return None

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
            if not message:
                return  # Ignore empty messages

            # Create message in DB (only sender)
            date = await self.create_message(message, self.user, self.group)
            if not date:
                return

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "name": self.user.get_full_name(),
                    "email": self.user.email,
                    "date": str(date),
                    "groupeName": self.room_name,
                }
            )
        except Exception as e:
            pass  # You can log error here

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "emailFrom": event["email"],
            "nameFrom": event["name"],
            "date": event["date"],
            "groupeName": event["groupeName"]
        }))
