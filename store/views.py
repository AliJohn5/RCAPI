
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
from django.db.models import Q, Value, IntegerField, Case, When
from users.models import Permission
from django.db.models.functions import Lower

@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    return Response(data={"test":"ok"})



@api_view(['GET'])
@permission_classes([AllowAny])
def initialize_permissions(request):
    permissions_to_init = [
        ("login", "User with this permission can login"),
        ("register", "User with this permission can register users"),
        ("list-users", "User with this permission can list all users"),
        ("list-all-groups", "User with this permission can see all created groups with members"),
        ("create-group", "User with this permission can create a new group"),
        ("upgrade-user", "User with this permission can upgrade users and give them permissions"),
        ("create-post", "User with this permission can create or delete posts"),
        ("notification", "User with this permission can send permission to users"),
        ("read-some-thing", "User with this permission can see materials in the closets and projects"),
        ("read-private-some-thing", "User with this permission can see private materials"),
        ("write-some-thing", "User with this permission can edit, delete, and create materials"),
        ("read-borrow", "User with this permission can see all borrowed"),
        ("write-borrow", "User with this permission can accept borrow"),
        ("read-closet", "User with this permission can read all closets"),
        ("read-mytype", "User with this permission can read all types"),
        ("write-closet", "User with this permission can create, delete, or edit closets"),
        ("write-mytype", "User with this permission can create, delete, or edit types"),
        ("read-proj", "User with this permission can read projects"),
        ("write-proj", "User with this permission can write, edit, and delete projects"),
        ("work", "User with this permission can work on projects"),
    ]

    for code, description in permissions_to_init:
        Permission.objects.get_or_create(
            permission=code,
            defaults={"description": description}
        )

    return Response(status=status.HTTP_200_OK)

### read data from models
@api_view(['GET'])
@permission_classes([HasPermission("login"),HasPermission("read-closet")])
@authentication_classes([TokenAuthentication])
def closets(request,i1,i2):
    closets = Closet.objects.all()[i1:i2]
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


@api_view(['GET'])
@permission_classes([HasPermission("login"),HasPermission("read-mytype")])
@authentication_classes([TokenAuthentication])
def mytypes(request,i1,i2):
    data = Type.objects.all()[i1:i2]
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
def projects(request,i1,i2):
    data = Project.objects.all()[i1:i2]
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



@api_view(['GET'])
@permission_classes([HasPermission("login"),HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings(request,i1,i2):
    user = request.user
    isPrivate = user.permissions.filter(permission = "read-private-some-thing").exists()

    if(isPrivate):
        data = SomeThing.objects.all()[i1:i2]
    else:
        data = SomeThing.objects.filter(isPrivate = False)[i1:i2]
    
    ser = SomeThingSerializer(data,many = True)

    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([HasPermission("login"),HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def somethings_search(request,i1,i2):
    user = request.user
    isPrivate = user.permissions.filter(permission = "read-private-some-thing").exists()
    query = request.data['q'].strip().lower()


    can_read_private = user.permissions.filter(permission="read-private-some-thing").exists()

    base_filter = Q(name__icontains=query) | \
                  Q(closet__name__icontains=query) | \
                  Q(mytype__name__icontains=query) | \
                  Q(project__name__icontains=query)

    if not can_read_private:
        base_filter &= Q(isPrivate=False)

    # Get results with relevance
    results = SomeThing.objects.annotate(
         relevance=(
            Case(When(name__iexact=query, then=Value(100)), default=Value(0), output_field=IntegerField()) +
            Case(When(name__icontains=query, then=Value(50)), default=Value(0), output_field=IntegerField()) +
            Case(When(closet__name__iexact=query, then=Value(80)), default=Value(0), output_field=IntegerField()) +
            Case(When(closet__name__icontains=query, then=Value(40)), default=Value(0), output_field=IntegerField()) +
            Case(When(mytype__name__iexact=query, then=Value(60)), default=Value(0), output_field=IntegerField()) +
            Case(When(mytype__name__icontains=query, then=Value(30)), default=Value(0), output_field=IntegerField()) +
            Case(When(project__name__iexact=query, then=Value(60)), default=Value(0), output_field=IntegerField()) +
            Case(When(project__name__icontains=query, then=Value(30)), default=Value(0), output_field=IntegerField())
        )
    ).filter(base_filter).order_by("-relevance")[i1:i2]

    ser = SomeThingSerializer(results,many = True)
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
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-mytype")])
@authentication_classes([TokenAuthentication])
def create_mytype(request):
    seri = TypeSerializer(data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,status=status.HTTP_201_CREATED)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-proj")])
@authentication_classes([TokenAuthentication])
def create_proj(request):
    seri = ProjectSerializer(data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,status=status.HTTP_201_CREATED)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-some-thing")])
@authentication_classes([TokenAuthentication])
def create_thing(request):
    seri = SomeThingSerializer(data=request.data)

    mytype = get_object_or_404(Type, name = request.data['mytype'])

    closet , project = None,None


    if(request.data['project'] != "None" and request.data['project'] != ""):
        project = get_object_or_404(Project , name = request.data['project'])

    if(request.data['closet'] != "None" and request.data['closet'] != ""):
        closet = get_object_or_404(Closet, name = request.data['closet'])

    if seri.is_valid():
        
        something = seri.save(mytype = mytype)

        if(project):
            something.project = project
        if(closet):
            something.closet = closet
        
        images = request.FILES.getlist('images')
        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Create PostImage with uploaded image filename (assuming you're storing file_name somewhere)
            SomeThingImage.objects.create(someThing=something, image=image_info['file_name'])
        
        seri = SomeThingSerializer(SomeThing.objects.get(pk = something.pk))
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
def edit_proj(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Validate and fetch workers
    worker_emails = request.data.getlist('workers', [])
    
    workers = [
        get_object_or_404(RCUser, email=email)
        for email in worker_emails
    ]


    # Prepare serializer data
    data = {
        'completion_rate': request.data.get('completion_rate'),
        'name': request.data.get('name'),
    }

    serializer = ProjectSerializer(project, data=data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj = serializer.save()
    obj.workers.clear()

    for i in workers:
        obj.workers.add(i)
    obj.save()
    

    # Handle images
    images = request.FILES.getlist('images', [])

    if images:
        # Delete old images in one query
        ProjectImage.objects.filter(project=project).delete()

        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response(
                    {'error': 'Image upload failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ProjectImage.objects.create(
                project=project,
                image=image_info['file_name']
            )

    return Response(serializer.data, status=status.HTTP_200_OK)

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

    seri = SomeThingSerializer(
        data,
        data=d,
        )
    if seri.is_valid():
        ob = seri.save()

        typ =  get_object_or_404(Type ,name=request.data['mytype'] )
        ob.mytype = typ

        if(request.data['project'] != "" and request.data['project'] != "None"):
            proj =   get_object_or_404(Project ,name=request.data['project'] )
            ob.project = proj
        else:
            ob.project = None
        
        if(request.data['closet'] != "" and request.data['closet'] != "None"):
            closet =   get_object_or_404(Closet ,name=request.data['closet'] )
            ob.closet = closet
        else:
            ob.closet=None


        ob.save()

        images = request.FILES.getlist('images', [])

        if images:
            # Delete old images in one query
            SomeThingImage.objects.filter(someThing=ob).delete()

            for img in images:
                image_info = upload_image_to_backblaze(img)
                if not image_info:
                    return Response(
                        {'error': 'Image upload failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                SomeThingImage.objects.create(
                    someThing=ob,
                    image=image_info['file_name']
                )

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
    elif (obj[0].is_returned):
        obj[0].delete()
        data.delete()
        return Response(status=status.HTTP_200_OK)
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





@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def get_info(request):
    projects = Project.objects.all()
    closets = Closet.objects.all()
    mytypes = Type.objects.all()

    ans = []
    for i in projects:
        ans.append({'type':"project","content":i.name})
    
    for i in closets:
        ans.append({'type':"closet","content":i.name})

    for i in mytypes:
        ans.append({'type':"type","content":i.name})

    return Response(ans, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission("login"), HasPermission("read-some-thing")])
@authentication_classes([TokenAuthentication])
def get_proj_info(request,pk):

    proj = get_object_or_404(Project,pk=pk)
    per = Permission.objects.get(permission="work")
    users = RCUser.objects.filter(Q(permissions=per))
    somthings = SomeThing.objects.filter(Q(project=proj))
    

    ans = []
    for i in users:
        ans.append({'type':"worker","content":i.email})
    
    for i in somthings:
        ans.append({'type':"something","content": SomeThingSerializer(i).data})

    return Response(ans, status=status.HTTP_200_OK)