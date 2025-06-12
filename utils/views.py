from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.response import Response
from users.permissions import HasPermission
from rest_framework import status

from users.utils import upload_image_to_backblaze
from .models import *
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated,AllowAny
from django.shortcuts import get_object_or_404


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-borrow")])
@authentication_classes([TokenAuthentication])
def list_borrows(request):
    bor = Borrow.objects.all()
    ser = BorrowSerializer(bor,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-borrow")])
@authentication_classes([TokenAuthentication])
def list_returned_borrows(request):
    bor = Borrow.objects.filter(is_returned = True)
    ser = BorrowSerializer(bor,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-borrow")])
@authentication_classes([TokenAuthentication])
def list_available_borrows(request):
    bor = Borrow.objects.filter(is_returned = False)
    ser = BorrowSerializer(bor,many = True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("read-borrow")])
@authentication_classes([TokenAuthentication])
def list_borrows_pk(request,pk):
    bor = get_object_or_404(Borrow,pk=pk)
    ser = BorrowSerializer(bor,many = False)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-borrow")])
@authentication_classes([TokenAuthentication])
def create_borrow(request):
    something = get_object_or_404(SomeThing,pk =request.data["something"])
    person = get_object_or_404(RCUser,email =request.data["person"] )
    if(something.borrowed):
        return Response(status=status.HTTP_303_SEE_OTHER)
    
    something.borrowed = True

    item = Borrow.objects.create(
        something = something,
    )
    item.person.add(person)
    item.save()

    seri = BorrowSerializer(item)
    return Response(seri.data,status=status.HTTP_201_CREATED)
    #return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("write-borrow")])
@authentication_classes([TokenAuthentication])
def return_borrow(request,pk):
    try:
        data = Borrow.objects.get(pk=pk)
    except:
        Borrow.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data.is_returned = True
    seri = BorrowSerializer(data,data=request.data)
    if seri.is_valid():
        seri.save()
        return Response(seri.data,
                            status=status.HTTP_200_OK)
    return Response(seri.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("write-borrow")])
@authentication_classes([TokenAuthentication])
def delete_borrow(request,pk):
    try:
        data = Borrow.objects.get(pk=pk)
    except:
        Borrow.DoesNotExist
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data.delete()
    return Response(status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([HasPermission("login"),HasPermission("create-post")])
@authentication_classes([TokenAuthentication])
def create_post(request):
    user = request.user
    
    # Initialize serializer with post data
    serializer = PostSerializer(data=request.data,)

    if serializer.is_valid():
        # Save the post instance first
        post = serializer.save(author=user)

        # Handle image uploads if any
        images = request.FILES.getlist('images')  # use getlist to handle multiple files
        for img in images:
            image_info = upload_image_to_backblaze(img)
            if not image_info:
                return Response({'error': 'Image upload failed'}, status=status.HTTP_400_BAD_REQUEST)

            # Create PostImage with uploaded image filename (assuming you're storing file_name somewhere)
            PostImage.objects.create(post=post, image=image_info['file_name'])

        # Re-serialize the post to include the images
        output_serializer = PostSerializer(post, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    

    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['Get'])
@permission_classes([AllowAny])
def get_post(request,pk):
    post = get_object_or_404(Post,pk = pk)
    output_serializer = PostSerializer(post, context={'request': request})
    return Response(output_serializer.data, status=status.HTTP_200_OK)



@api_view(['Get'])
@permission_classes([AllowAny])
def list_posts(request,i1,i2):
    post = Post.objects.all()
    output_serializer = PostSerializer(post, many = True,context={'request': request})
    return Response(output_serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([HasPermission("login"),HasPermission("create-post")])
@authentication_classes([TokenAuthentication])
def delete_post(request,pk):
    post = get_object_or_404(Post,pk = pk)
    post.delete()
    return Response(status=status.HTTP_200_OK)