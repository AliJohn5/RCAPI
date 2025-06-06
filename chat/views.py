from datetime import timedelta
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
from django.utils import timezone
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
        ).order_by('-date')

        if(len(mess) > 0):
            try:
                author = mess[0].author
            except RCUser.DoesNotExist:
                author = None
            
            ans.append({
                    'author': {
                        'email': author.email if author else 'deleted email',
                        'last_name': author.first_name if author else '',
                        'first_name': author.last_name if author else ''
                    },
                    'content': mess[0].content,
                    'date': str(mess[0].date),
                    'group': group.name
                })
        else:
            ans.append({'group':group.name})

        
    return Response(ans[i1 : i2],status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([HasPermission("list-all-groups")])
@authentication_classes([TokenAuthentication])
def groups_list_all(request, i1, i2):
    try:
        i1 = int(i1)
        i2 = int(i2)
    except ValueError:
        return Response({"error": "Invalid range parameters."}, status=status.HTTP_400_BAD_REQUEST)

    if i1 < 0 or i2 <= i1:
        return Response({"error": "Invalid range values."}, status=status.HTTP_400_BAD_REQUEST)

    data = MyGroup.objects.all()
    ans = []

    for group in data:
        tmp = {
            'group': group.name,
            'members': [mem.email for mem in group.members.all()]
        }
        ans.append(tmp)

    return Response(ans[i1:i2], status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("create-group")])
@authentication_classes([TokenAuthentication])
def groups_create(request):
    group = MyGroupSerializer(data =request.data)
    #mem = []
    #for email in request.data['members']:
    #    mem.append(get_object_or_404(RCUser,email=email))

    if( group.is_valid()):
        group.save()
        #obj = MyGroup.objects.get(pk = group.data["pk"])
        #for user in mem:
        #    obj.members.add(user)
        return Response(status=status.HTTP_200_OK)
#        return Response( MyGroupSerializer(obj,many = False).data,status=status.HTTP_200_OK)
    return Response(group.errors,status=status.HTTP_400_BAD_REQUEST)



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
        obj.members.clear()
        for user in mem:
            obj.members.add(user)

        return Response(status=status.HTTP_200_OK)
    return Response(group.errors,status=status.HTTP_400_BAD_REQUEST)
    
    


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

   
@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("create-group")])
@authentication_classes([TokenAuthentication])
def create_group_code(request):
    serializer = GroupCodeSerializer(data=request.data)
    if serializer.is_valid():
        group = GroupCode(group_name=serializer.validated_data['group_name'])
        group.save()
        return Response(GroupCodeSerializer(group).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login")])
@authentication_classes([TokenAuthentication])
def join_group_by_code(request):

    groupcode = get_object_or_404(GroupCode,code = request.data['code'])
    # Check if code is expired
    if timezone.now() - groupcode.date > timedelta(hours=24):
        groupcode.delete()
        return Response({'error': 'This code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    group = get_object_or_404(MyGroup,name = groupcode.group_name)

    group.members.add(user)

    return Response( status=status.HTTP_200_OK)
    
    