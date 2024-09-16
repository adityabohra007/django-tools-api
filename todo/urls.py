from .apiview import *
from django.urls import path

urlpatterns = [
    path("create", TodoApiView.as_view()),
    path("list/", TodoListApiView.as_view(), name=""),
    path("<int:pk>", TodoUpdateDetailApiView.as_view(), name=""),
    path("todolist/create", TodoListCreateApiView.as_view()),
    path("todolist/<int:pk>", TodoListUpdateDetailApiView.as_view()),
]
