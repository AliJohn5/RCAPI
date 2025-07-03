from datetime import timedelta
import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from .serializers import RCUserSerializer
from .permissions import HasPermission
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import  AllowAny
import random,string
from django.conf import settings
from django.db.models import Q
from rest_framework.permissions import  IsAuthenticated,AllowAny
import random, string
from django.core.mail import EmailMessage
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage
from .utils import get_b2_signed_url, upload_image_to_backblaze


def generate_random_string(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def send_code_email(to_email, code):
    try:
        subject = 'Robotic Club code'
        html_message = f'''
    <div style="max-width: 600px; margin: auto; padding: 30px; background-color: #f9f9f9; border-radius: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
        <div style="text-align: center; padding-bottom: 20px;">
            <h2 style="margin: 0; color: #2c3e50;">🤖 Robotic Club</h2>
            <p style="font-size: 14px; color: #888;">Verification Code</p>
        </div>
        <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
            <p>Hi there 👋,</p>
            <p>Here is your one-time code to access the Robotic Club:</p>
            <p style="font-size: 32px; font-weight: bold; text-align: center; color: #2c3e50; letter-spacing: 2px;">{code}</p>
            <p>This code can only be used once and will expire soon.</p>
            <p>If you didn’t request this code, you can safely ignore this email.</p>
        </div>
        <div style="text-align: center; margin-top: 30px; font-size: 14px; color: #999;">
            <p>Thanks,<br>The Robotic Club Team</p>
        </div>
    </div>
'''

        email = EmailMessage(subject, html_message, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.content_subtype = "html"  # Important: this tells Django it's an HTML email
        email.send()
        return "OK"
    except Exception as e:
        return f'NOTOK {str(e)}'




@api_view(['POST'])
@permission_classes([HasPermission("register")])
@authentication_classes([TokenAuthentication])
def accept_register(request): 
    login_permission = get_object_or_404( Permission, permission='login')
    user = get_object_or_404(RCUser,email = request.data['email'])
    
    user.permissions.add(login_permission)
    user.save()
    serializer = RCUserSerializer(user)
    
    
    return Response(serializer.data, status=status.HTTP_200_OK)
    



@api_view(['POST'])
@permission_classes([HasPermission("register")])
@authentication_classes([TokenAuthentication])
def get_register(request):
    loginper = Permission.objects.get(permission = 'login')
    users = RCUser.objects.filter(~Q(permissions = loginper))
    emails = { }
    for user in users:
        emails[user.id] = user.email
    return Response(emails, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasPermission("list-users")])
@authentication_classes([TokenAuthentication])
def get_users(request):
    users = RCUser.objects.all()
    ser = RCUserSerializer(users, many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def RegisterView(request):
    data = request.data
    data['permissions'] = []
    serializer = RCUserSerializer(data=data)
    
    if serializer.is_valid():
        
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        PermissionRequest.objects.create(
                user = user,
                permission = "login"
            )
        return Response({
            'id': user.pk,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class Login(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if not user.permissions.filter(permission='login').exists():
            return Response({"details":"Please visit Robotic Club in Latakia university, to confirm your account.\nYou can't login now!!"},status=status.HTTP_401_UNAUTHORIZED)

        
        

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'access_token': token.key,
            'id': user.pk,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'phone_number':user.phone_number,
            'image_url':user.image.url if user.image else "No"
        },status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def GenerateCodeView(request):
    user = RCUser.objects.get(email = request.data['email'])
    if(user):
        oldcode = Code.objects.filter(user=user)
        for obj in oldcode:
            obj.delete()
        
        code = Code.objects.create(
            code = generate_random_string(10),
            user = user
        )
        if(send_code_email(request.data['email'],code=code.code) == "OK"):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(  data={'details' : 'cant send email'},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response( status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def ForgetPasswordView(request):
    user = RCUser.objects.get(email = request.data['email'])
    newpassword =  request.data['password']
    realcode = Code.objects.get(user=user).code
    reccode = request.data['code']

    if(user):
        if(realcode != reccode):
            return Response( data={'details' : 'wrong code'},status=status.HTTP_401_UNAUTHORIZED)
        user.set_password(newpassword)
        user.save()
        obj = get_object_or_404(Code,user = user)
        obj.delete()

        return Response(status=status.HTTP_200_OK)
        
    else:
        return Response( status=status.HTTP_404_NOT_FOUND)
    




@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login")])
@authentication_classes([TokenAuthentication])
def upload_user_image(request):
    user = request.user

    # Upload new image to Backblaze
    image = upload_image_to_backblaze(request.FILES['image'])
    if not image:
        return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user model's image field (assuming it's a URLField or CharField)
    
    user.image = image['file_name']
    user.signed_url = image['signed_url']
    user.signed_url_generated_at = timezone.now
    user.save()

    # Return updated user info using serializer
    serializer = RCUser(user)
    return Response({
        'message': 'Image uploaded successfully',
        'image_url': image['signed_url'],
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login")])
@authentication_classes([TokenAuthentication])
def get_user_image(request, email):
    try:
        project = RCUser.objects.get(email=email)
    except RCUser.DoesNotExist:
        return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
    
    now = timezone.now()

    if project.signed_url and project.signed_url_generated_at:
            if now - project.signed_url_generated_at > timedelta(days=5):
                return Response({'image':project.signed_url}, status=status.HTTP_200_OK)
            

    new_signed_url = get_b2_signed_url(project.image.name)
    project.signed_url = new_signed_url
    project.signed_url_generated_at = now
    project.save(update_fields=["signed_url", "signed_url_generated_at"])

    return Response({'image':new_signed_url}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, HasPermission("login")])
@authentication_classes([TokenAuthentication])
def modify_user_data(request):
    user = request.user
    seri = RCUserSerializer(user,data=request.data, partial=True)
    if seri.is_valid():
        seri.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("upgrade"),HasPermission("login")])
@authentication_classes([TokenAuthentication])
def upgarde_user(request, email):
    user = get_object_or_404(RCUser,email = email)
    perm = []
    for item in request.data['per']:
       perm.append( get_object_or_404(Permission,permission = item) )

    for item in perm:
        user.permissions.add(item)
    
    user.save()
    return Response( status=status.HTTP_200_OK)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("upgrade"), HasPermission("login")])
@authentication_classes([TokenAuthentication])
def downgrade_user(request, email):
    user = get_object_or_404(RCUser,email = email)
    perm = []
    for item in request.data['per']:
       perm.append( get_object_or_404(Permission,permission = item) )

    for item in perm:
        user.permissions.remove(item)
    
    user.save()
    return Response( status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("write-per"), HasPermission("login")])
@authentication_classes([TokenAuthentication])
def write_per(request):
    per = PermissionSerializer(data = request.data)
    if(per.is_valid()):
        per.save()
        return Response(data=per.data, status=status.HTTP_200_OK)
    else:
        return Response( status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("read-per"), HasPermission("login")])
@authentication_classes([TokenAuthentication])
def read_per(request):
    per = PermissionSerializer(Permission.objects.all(),many = True)
    return Response(data=per.data, status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission("login")])
@authentication_classes([TokenAuthentication])
def list_permissions(request):

    ans = {
        'permissions':[],
        'myPermissions':[],
        'pendingPermissions':[],
    }

    user = request.user
    permissions = Permission.objects.all()
    myPermissions = user.permissions.all()
    pendingPermissions = PermissionRequest.objects.filter(user = user)

    for per in permissions:
        ans['permissions'].append( per.permission )
    
    for per in myPermissions:
        ans['myPermissions'].append( per.permission )

    for per in pendingPermissions:
        ans['pendingPermissions'].append( per.permission )    

    return Response(ans,status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission("login"),HasPermission("upgrade-user")])
@authentication_classes([TokenAuthentication])
def list_pending_permissions(request,i1,i2):
    pendingPermissionsSerializer = PermissionRequestSerialiser(PermissionRequest.objects.all()[i1:i2],many = True)
    return Response(pendingPermissionsSerializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login")])
@authentication_classes([TokenAuthentication])
def send_pending_permissions(request):
    user = request.user
    permissions = request.data['permissions']

    for per in permissions:
        try:
            PermissionRequest.objects.create(
                user = user,
                permission = per
            )
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
   
    return Response(status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("login"),HasPermission("upgrade-user")])
@authentication_classes([TokenAuthentication])
def action_pending_permissions(request):

    for data in request.data:
        pk = data['pk']
        action = data['action']
        req = get_object_or_404(PermissionRequest,pk=pk)

        if(action == 'delete'):
            req.delete()

        elif(action == 'accept'):
            user = req.user
            permission = get_object_or_404(Permission,permission=req.permission)
            user.permissions.add(permission)
            user.save()
            req.delete()
        else:
            return Response({'unknown action' : action},status=status.HTTP_400_BAD_REQUEST)
   
    return Response(status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPermission("upgrade-user")])
@authentication_classes([TokenAuthentication])
def list_users_permissions(request,i1,i2):

    ans = {
        'permissions':[],
        'users':[],
    }

    permissions = Permission.objects.all()
    users = RCUser.objects.all()[i1:i2]

    for per in permissions:
        ans['permissions'].append( per.permission )
    
    for user in users:
        data = {}
        data['user'] = user.email
        data['permissions'] = []
        per = user.permissions.all()
        for x in per:
            data['permissions'].append(x.permission)
        ans['users'].append(data)

    return Response(ans,status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPermission("upgrade-user")])
@authentication_classes([TokenAuthentication])
def upgrade_users_permissions(request):

    for data in request.data:
        user = get_object_or_404(RCUser,email = data['user'])
        user.permissions.clear()
        
        for perm in data['permissions']:
            x = get_object_or_404(Permission,permission = perm)
            user.permissions.add(x)
        user.save()
        
    return Response(status=status.HTTP_200_OK)
