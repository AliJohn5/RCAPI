from .views import *
from django.urls import path

urlpatterns = [
    path("borrow/",list_borrows),
    path("borrow/returned/",list_returned_borrows),
    path("borrow/available/",list_available_borrows),
    path("borrow/<int:pk>",list_borrows_pk),
    path("borrow/return/<int:pk>",return_borrow),
    path("borrow/create/",create_borrow),
    path("borrow/delete/<int:pk>",delete_borrow),

    path("post/create/",create_post),
    path("post/list/<int:i1>/<int:i2>",list_posts),
    path("post/delete/<int:pk>",delete_post),
    path("post/get/<int:pk>",get_post),






]