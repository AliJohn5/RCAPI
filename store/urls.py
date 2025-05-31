from .views import *
from django.urls import path

urlpatterns = [

    path('test/',test),

    # read (list, one)
    path('closets/',closets),
    path('closets/<int:pk>',closets_pk),
    path('mytypes/',mytypes),
    path('mytypes/<int:pk>',mytypes_pk),
    path('projects/',projects),
    path('projects/<int:pk>',projects_pk),
    path('somethings/',somethings),
    path('somethings/<int:pk>',somethings_pk),
    path('somethingsp/',somethings_private),
    path('somethingsp/<int:pk>',somethings_private_pk),

    # add one
    path('create_closet/',create_closet),
    path('create_mytype/',create_mytype),
    path('create_proj/',create_proj),
    path('create_thing/',create_thing),

   
    


    # edit
    path('edit_closet/<int:pk>',edit_closet),
    path('edit_mytype/<int:pk>',edit_mytype),
    path('edit_proj/<int:pk>',edit_proj),
    path('edit_thing/<int:pk>',edit_thing),



    #delete
    path('delete_closet/<int:pk>',delete_closet),
    path('delete_mytype/<int:pk>',delete_mytype),
    path('delete_proj/<int:pk>',delet_proj),
    path('delete_thing/<int:pk>',delete_thing),


    #related
    path('related_closet/<int:pk>',related_closet),
    path('related_mytype/<int:pk>',related_mytype),
    path('related_proj/<int:pk>',related_proj),
    path('related_user/<str:email>',related_user),

    #images
    path('upload-project-image/<int:id>', upload_project_image, name='upload_project_image'),
    path('get-project-image/<int:id>', get_project_image, name='get_project_image'),
    path('upload-something-image/<int:id>', upload_something_image, name='upload_something_image'),
    path('get-something-image/<int:id>', get_something_image, name='get_something_image'),



]
