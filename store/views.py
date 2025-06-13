
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from users.permissions import HasPermission
from rest_framework import status

from users.utils import upload_image_to_backblaze
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated,AllowAny
from users.permissions import HasPermission
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from utils.models import Borrow
from django.db.models import Q

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def test(request):
    return Response(data={"test":"ok"})




### read data from models
@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-closet")])
@authentication_classes([TokenAuthentication])
def closets(request):
    closets = Closet.objects.all()
    ser = ClosetSerializer(closets,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-closet")])
@authentication_classes([TokenAuthentication])
def closets_pk(request,pk):
    try:
        data = Closet.objects.get(pk=pk)
    except:
        Closet.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    ser = ClosetSerializer(data,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-mytype")])
@authentication_classes([TokenAuthentication])
def mytypes(request):
    data = Type.objects.all()
    ser = TypeSerializer(data,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-mytype")])
@authentication_classes([TokenAuthentication])
def mytypes_pk(request,pk):
    try:
        data = Type.objects.get(pk=pk)
    except:
        Type.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    ser = TypeSerializer(data,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-proj")])
@authentication_classes([TokenAuthentication])
def projects(request):
    data = Project.objects.all()
    ser = ProjectSerializer(data,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-proj")])
@authentication_classes([TokenAuthentication])
def projects_pk(request,pk):
    try:
        data = Project.objects.get(pk=pk)
    except:
        Project.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    ser = ProjectSerializer(data,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings(request):
    data = SomeThing.objects.filter(isPrivate=False)
    ser = SomeThingSerializer(data,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings_pk(request,pk):
    try:
        data = SomeThing.objects.get(pk=pk)
    except:
        SomeThing.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if(data.isPrivate == True):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    ser = SomeThingSerializer(data,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-private-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings_private(request):
    data = SomeThing.objects.all()
    ser = SomeThingSerializer(data,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-private-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings_private_pk(request,pk):
    data = SomeThing.objects.get(pk=pk)
    ser = SomeThingSerializer(data,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)




### create data to models

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-closet")])
@authentication_classes([TokenAuthentication])
def create_closet(request):
    serializer = ClosetSerializer(data=request.data)

    if serializer.is_valid():
        # Save the post instance first
        closet = serializer.save()

        # Handle image uploads if any
        images = request.FILES.getlist('images')  # use getlist to handle multiple files
        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Create PostImage with uploaded image filename (assuming you're storing file_name somewhere)
            ClosetImage.objects.create(closet=closet, image=image_info['file_name'])

        # Re-serialize the post to include the images
        output_serializer = ClosetSerializer(closet, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-mytype")])
@authentication_classes([TokenAuthentication])
def create_mytype(request):
    seri = TypeSerializer(data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-proj")])
@authentication_classes([TokenAuthentication])
def create_proj(request):
    seri = ProjectSerializer(data=request.data)
    workers = []
    for wr in request.data["workers"]:
        workers.append(get_object_or_404(RCUser,email = wr))
    
    project = seri
    if seri.is_valid():
        seri.save()
        obj = Project.objects.get(pk = seri.data["pk"])
        for wr in workers:
            obj.workers.add(wr)
        project =  obj.save()

        images = request.FILES.getlist('images')  # use getlist to handle multiple files
        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Create PostImage with uploaded image filename (assuming you're storing file_name somewhere)
            ProjectSerializer.objects.create(project=project, image=image_info['file_name'])

        seri = ProjectSerializer(project)
        return Response(seri.data,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-some-thing")])
@authentication_classes([TokenAuthentication])
def create_thing(request):
    seri = SomeThingSerializer(data=request.data)

    closet = get_object_or_404(Closet, pk = request.data['closet'])
    mytype = get_object_or_404(Type, pk = request.data['mytype'])
    project = get_object_or_404(Project , pk = request.data['project'])

    if seri.is_valid():
        something = seri.save(closet = closet,mytype = mytype,project = project)
        images = request.FILES.getlist('images')  # use getlist to handle multiple files
        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Create PostImage with uploaded image filename (assuming you're storing file_name somewhere)
            SomeThingImage.objects.create(someThing=something, image=image_info['file_name'])
        return Response(seri.data,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



## edit 

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-closet")])
@authentication_classes([TokenAuthentication])
def edit_closet(request,pk):
    data = get_object_or_404(Closet,pk=pk)
    seri = ClosetSerializer(data,data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,
                            status=status.HTTP_200_OK)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-mytype")])
@authentication_classes([TokenAuthentication])
def edit_mytype(request,pk):
    data = get_object_or_404(Type,pk=pk)
    seri = TypeSerializer(data,data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,
                            status=status.HTTP_200_OK)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-proj")])
@authentication_classes([TokenAuthentication])
def edit_proj(request,pk):
    data = get_object_or_404(Project,pk=pk)
    d = {}
    d['completion_rate'] = request.data['completion_rate']
    d['name'] = request.data['name']
    d['number_of_some_things'] = request.data['number_of_some_things']
    
    workers = []
    for em in request.data['workers']:
        workers.append(get_object_or_404(RCUser,email = em))    
    d['workers'] = workers
    
    seri = ProjectSerializer(data,data = d)

    if seri.is_valid():
        seri.save()
        return Response(seri.data,
                            status=status.HTTP_200_OK)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-some-thing")])
@authentication_classes([TokenAuthentication])
def edit_thing(request,pk):
    data = get_object_or_404(SomeThing,pk=pk)

    d = {}

    d['name'] =     request.data['name']
    d['isActive']=  request.data['isActive'] 
    d['isPrivate']= request.data['isPrivate']  
    d['borrowed']=  request.data['borrowed'] 

    d['mytype'] =   get_object_or_404(Type ,pk=request.data['mytype'] )
    d['project']=   get_object_or_404(Project ,pk=request.data['project'] )
    d['closet'] =   get_object_or_404(Closet ,pk=request.data['closet'])

    seri = SomeThingSerializer(data,data=d)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,
                            status=status.HTTP_200_OK)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)





#delete


@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("write-closet")])
@authentication_classes([TokenAuthentication])
def delete_closet(request,pk):
    data = get_object_or_404(Closet,pk=pk)
    data.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("write-mytype")])
@authentication_classes([TokenAuthentication])
def delete_mytype(request,pk):
    data = get_object_or_404(Type,pk=pk)
    data.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("write-proj")])
@authentication_classes([TokenAuthentication])
def delet_proj(request,pk):
    data = get_object_or_404(Project,pk=pk)
    data.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("write-some-thing")])
@authentication_classes([TokenAuthentication])
def delete_thing(request,pk):
    data = get_object_or_404(SomeThing,pk=pk)
    obj = Borrow.objects.filter(Q(something = data))
                             
    if(not obj):
        data.delete()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_423_LOCKED)

## related
@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-mytype")])
@authentication_classes([TokenAuthentication])
def related_mytype(request,pk):
    data = get_object_or_404(Type,pk=pk)
    related_somethings = data.mytype_somethings.all()
    seri = SomeThingSerializer(related_somethings,many = True)
    return Response(seri.data,status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-closet")])
@authentication_classes([TokenAuthentication])
def related_closet(request,pk):
    data = get_object_or_404(Closet,pk=pk)
    related_somethings = data.closet_somethings.all()
    seri = SomeThingSerializer(related_somethings,many = True)
    return Response(seri.data,status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-proj")])
@authentication_classes([TokenAuthentication])
def related_proj(request,pk):
    data = get_object_or_404(Closet,pk=pk)
    related_somethings = data.project_somethings.all()
    seri = SomeThingSerializer(related_somethings,many = True)
    return Response(seri.data,status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-proj")])
@authentication_classes([TokenAuthentication])
def related_user(request,email):
    data = get_object_or_404(RCUser,email=email)
    related_somethings = data.projects.all()
    seri = ProjectSerializer(related_somethings,many = True)
    return Response(seri.data,status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("write-proj")])
@authentication_classes([TokenAuthentication])
def upload_project_image(request,id):
    project = get_object_or_404(Project,pk=id)
    serializer = ProjectImageSerializer(project, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("read-proj")])
@authentication_classes([TokenAuthentication])
def get_project_image(request, id):
    project = get_object_or_404(Project,pk=id)
    serializer = ProjectImageSerializer(project,context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)



@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("write-some-thing")])
@authentication_classes([TokenAuthentication])
def upload_something_image(request,id):
    project = get_object_or_404(SomeThing,pk=id)
    serializer = SomeThingImageSerializer(project, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def get_something_image(request, id):
    project = get_object_or_404(SomeThing,pk=id)
    serializer = SomeThingImageSerializer(project,context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)