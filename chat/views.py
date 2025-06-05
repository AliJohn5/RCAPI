from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from users.permissions import HasPermission
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated,AllowAny
from users.permissions import HasPermission
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import *
from .serializers import MyGroupSerializer



def isMember(user,group) -> bool:
    return group.members.filter(email = user.email).exists()


@api_view(['GET'])
@permission_classes([HasPermission("login")])
@authentication_classes([TokenAuthentication])
def mess(request,room_name,i1,i2):
    gr = get_object_or_404(MyGroup,name = room_name)
    if (not isMember(request.user,gr)):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    q = gr.mymessages.all()

    if(i1 > i2):
        return Response(status=status.HTTP_404_NOT_FOUND)

    if(len(q) <= i1 and len(q) <= i2):
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if(len(q) <= i2):
        i2 = len(q)
    q = q[i1:i2]

    mes = MessageSerializer( q,many = True )
    return Response(mes.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([HasPermission("login")])
@authentication_classes([TokenAuthentication])
def groups_list(request,i1,i2):
    user = request.user
    ans = []

    data = MyGroup.objects.filter(
        Q(members = user)
    )

    for group in data:
        mess = Message.objects.filter(
            Q(group=group)
        )
        if(len(mess) > 0):
            ans.append(
                {
                    'author':{
                        'email' : mess[0].author.email,
                        'last_name' : mess[0].author.first_name,
                        'first_name' : mess[0].author.last_name

                    },
                    'content' : mess[0].content,
                    'date' : str(mess[0].date),
                    'group':group.name
                }
            )
        else:
            ans.append({'group':group.name})

        
    return Response(ans[i1 : i2],status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("create-group")])
@authentication_classes([TokenAuthentication])
def groups_create(request):
    group = MyGroupSerializer(data =request.data)
    mem = []
    for email in request.data['members']:
        mem.append(get_object_or_404(RCUser,email=email))

    if( group.is_valid()):
        group.save()
        obj = MyGroup.objects.get(pk = group.data["pk"])
        for user in mem:
            obj.members.add(user)

        return Response( MyGroupSerializer(obj,many = False).data,status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("create-group")])
@authentication_classes([TokenAuthentication])
def groups_update(request,name):
    obj = get_object_or_404(MyGroup,name=name)
    
    group = MyGroupSerializer(obj,data=request.data)
    mem = []
    for email in request.data['members']:
        mem.append(get_object_or_404(RCUser,email=email))
        
    if( group.is_valid()):
        group.save()
        obj = MyGroup.objects.get(pk = group.data["pk"])
        for user in mem:
            obj.members.add(user)

        return Response( MyGroupSerializer(obj,many = False).data,status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
    
    


@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("create-group")])
@authentication_classes([TokenAuthentication])
def groups_delete(request,name):
    obj = get_object_or_404(MyGroup,name=name)
    obj.delete()
    return Response(status=status.HTTP_200_OK)
    


@api_view(['POST'])
@permission_classes([HasPermission("login")])
@authentication_classes([TokenAuthentication])
def groups_list_name(request,name):
    obj = get_object_or_404(MyGroup,name=name)
    if (not isMember(request.user,obj)):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(MyGroupSerializer(obj ,many = False).data,status=status.HTTP_200_OK)

   
