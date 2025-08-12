from .views import *
from django.urls import path

urlpatterns = [

    path("borrow/all/<int:i1>/<int:i2>",list_borrows),
    path("borrow/accepted/<int:i1>/<int:i2>",list_borrows_accepted),
    path("borrow/pending/<int:i1>/<int:i2>",list_borrows_pending),
    path("borrow/user/<int:i1>/<int:i2>",list_borrows_user1),


    path("borrow/pending/",list_pending_borrows),
    path("borrow/available/",list_available_borrows),
    path("borrow/<int:pk>",list_borrows_pk),
    path("borrow/return/<int:pk>",return_borrow),
    path("borrow/accept/<int:pk>",accept_borrow),
    path("borrow/create/<int:pk>",create_borrow),


    path("post/create/",create_post),
    path("post/list/<int:i1>/<int:i2>",list_posts),
    path("post/list-web/<int:i1>/<int:i2>",list_posts_web),
    path("post/delete/<int:pk>",delete_post),
    path("post/get/<int:pk>",get_post),

]