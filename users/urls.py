from .views import *
from django.urls import path,include

urlpatterns = [
    path('register/',RegisterView),
    path('getregister/',get_register),
    path('acceptregister/',accept_register),

    path('modify/',modify_user_data),

    path('list/',get_users),
    path('login/',Login.as_view()),
    
    path('gencode/',GenerateCodeView),
    path('forgetpass/',ForgetPasswordView),
    path('upgrade/<str:email>',upgarde_user),
    path('downgrade/<str:email>',downgrade_user),

    path('write-per/',write_per),
    path('read-per/',read_per),



    path('upload-user-image/', upload_user_image, name='upload_something_image'),
    path('get-user-image/<str:email>', get_user_image, name='get_something_image'),


]
