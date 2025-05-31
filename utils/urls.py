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

]