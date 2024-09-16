from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework.response import Response
from .serializers import *
from rest_framework import status

# from .utils import parse_date, parse_datetime_with_timezone, time_left_in_seconds
from django.utils import timezone
from django.db import transaction

# from django.db.transaction import atomic
from .models import *
import datetime

# from .utils import check_if_any_timer_already_active
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.jwt_auth import JWTAuthentication, JWTCookieAuthentication

# right now working on guest user only

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


# Methods
class TodoApiView(APIView):

    def post(self, request):
        data = request.data
        serializers = CreateTodoSerializer(
            data={
                "user": request.user.id,
                "title": data["title"],
                "custom_color_code": data["custom_color_code"],
                "category": data["category"],
                "description": data["description"],
            }
        )
        if serializers.is_valid():
            serializers.save()
            return Response(status=status.HTTP_200_OK)


class TodoUpdateDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.filter()
    serializer_class = TodoSerializer

    def get_queryset(self):
        return super().get_queryset().filter()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TodoListApiView(generics.ListAPIView):

    serializer_class = TodoSerializer
    queryset = Todo.objects.filter()

    def get(self, request, *args, **kwargs):
        print("getting it")
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TodoListListApiView(generics.ListAPIView):
    serializer_class = TodoListSerializer
    queryset = TodoList.objects.filter()

    def get_queryset(self):
        return super().get_queryset()  # filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# class TodoListApiView(APIView):
#     def post(self, request):
#         serializers = TodoListCreateSerializer(data=request.data)
#         if serializers.is_valid():
#             serializers.save()


class TodoListCreateApiView(APIView):
    def post(self, request):
        data = request.data
        todo = Todo.objects.get(id=request.data["todo"])
        serializers = TodoListCreateSerializer(
            data={
                "user": request.user.id,
                "title": data["title"],
                # "custom_color_code": data["custom_color_code"],
                # "category": data["category"],
                "description": data["description"],
            }
        )
        if serializers.is_valid():
            instance = serializers.save()
            todo.todo_list.add(instance)
            todo.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)


class TodoListUpdateDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TodoList.objects.filter()
    serializer_class = TodoListUpdateSerializer

    def get_queryset(self):
        return super().get_queryset()

    def get_object(self):
        obj = super().get_object()
        print(obj.todo_set.values()[0]["user_id"])
        if obj.todo_set.values()[0]["user_id"] == self.request.user.id:
            return obj
        else:
            from django.shortcuts import get_object_or_404 as _get_object_or_404

            print("came in")
            # obj = _get_object_or_404(TodoList.objects.none(),0)

    def update(self, request, *args, **kwargs):
        print('in update',request.data)
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    # def destroy(self, request, *args, **kwargs):
    #     return super().destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
