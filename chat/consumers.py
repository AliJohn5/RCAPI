import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from users.models import RCUser
from .models import MyGroup,Message
from django.shortcuts import get_object_or_404
from channels.auth import login
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authtoken.models import Token
from asgiref.sync import sync_to_async
from .serializers import MessageSerializer
class ChatConsumer(AsyncWebsocketConsumer):
    
    @sync_to_async
    def getUser(self,token):
        return RCUser.objects.get(id =  Token.objects.get(key = token).user_id)
    
    @sync_to_async
    def isMember(self,user,group) -> bool:
        return group.members.filter(email = user.email).exists()
    
    @sync_to_async
    def getGroup(self,name):
        return MyGroup.objects.get(name=name)
    
    @sync_to_async
    def createMess(self,mess):
        d = {}
        d['content'] = mess
        seri = MessageSerializer(data = d)
        if seri.is_valid():
            seri.save(author = self.user)
            obj = Message.objects.get(pk = seri.data['pk'])
            obj.group.add(self.group)

            return obj.date, self.room_name
        else: return None,None

    async def connect(self):
        try :
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = f"chat_{self.room_name}"

            header = self.scope['headers']
            token = b''

            for i in header:
                if(i[0] == b'authorization'):
                    token = i[1]
                    break
                
                
            if(not token):
                await self.close()

            token = token.decode().split(' ')[1]

            try:
                self.user =  await self.getUser(token)
                self.group =  await self.getGroup(self.room_name)

                if(self.user and self.group):
                    if(await self.isMember(self.user,self.group)):
                        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
                        await self.accept()
                    else:
                        await self.close()
            except Exception as e:
                await self.close()
        except Exception as e:
                await self.close()
        return
        

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        nameFrom = self.user.first_name + " " + self.user.last_name
        emailFrom  = self.user.email
        date , groupeName= await self.createMess(message)
        if(date):
            await self.send(text_data=json.dumps({"message": message,"emailFrom" : emailFrom,"nameFrom":nameFrom,"date":str(date),'groupeName':groupeName}))
