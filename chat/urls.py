from django.urls import path

from . import views


urlpatterns = [
    path("groups/<int:i1>/<int:i2>", views.groups_list),     
    path("groups/<str:room_name>/", views.groups_list_name),
    path("<str:room_name>/<int:i1>/<int:i2>", views.mess),
    path("groups-create/", views.groups_create),
    path("groups-update/<str:name>", views.groups_update),
    path("groups-delete/<str:name>", views.groups_delete),
]